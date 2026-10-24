from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from statistics import mean, pstdev
from typing import Iterable, Mapping, Sequence

from chainbreaker.domain.enums import Stage
from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event

from .finding import DetectionFinding


@dataclass(frozen=True, slots=True)
class DeviceProfile:
    device_class: str
    allowed_peers: frozenset[str]
    allowed_commands: frozenset[str]
    period_mean: float
    period_std: float
    payload_mean: float
    payload_std: float
    maintenance_windows: tuple[tuple[time, time], ...] = ()


def build_profile(device_class: str, events: Sequence[Event], *, maintenance_windows: Sequence[tuple[time, time]] = ()) -> DeviceProfile:
    ordered = sorted((event for event in events if event.device_class == device_class), key=lambda event: event.timestamp)
    if not ordered:
        raise ValueError(f"no baseline events for {device_class}")
    intervals = [(b.timestamp - a.timestamp).total_seconds() for a, b in zip(ordered, ordered[1:]) if b.timestamp > a.timestamp] or [60.0]
    payloads = [float(event.payload_size or 0) for event in ordered]
    return DeviceProfile(
        device_class=device_class,
        allowed_peers=frozenset(event.peer for event in ordered if event.peer),
        allowed_commands=frozenset(event.command for event in ordered if event.command),
        period_mean=mean(intervals), period_std=max(pstdev(intervals) if len(intervals) > 1 else mean(intervals) * 0.1, 1.0),
        payload_mean=mean(payloads), payload_std=max(pstdev(payloads) if len(payloads) > 1 else mean(payloads) * 0.1, 1.0),
        maintenance_windows=tuple(maintenance_windows),
    )


def _z(value: float, center: float, spread: float) -> float:
    return abs(value - center) / max(spread, 1e-9)


def _in_window(value: time, start: time, end: time) -> bool:
    return start <= value <= end if start <= end else value >= start or value <= end


def detect_iot(events: Iterable[Event], profiles: Mapping[str, DeviceProfile], *, threshold: float = 3.0) -> list[DetectionFinding]:
    by_device: dict[str, list[Event]] = {}
    for event in events:
        if event.device_id and event.device_class:
            by_device.setdefault(event.device_id, []).append(event)
    findings: list[DetectionFinding] = []
    for device_id, device_events in by_device.items():
        previous: Event | None = None
        for event in sorted(device_events, key=lambda item: item.timestamp):
            profile = profiles.get(event.device_class or "")
            if not profile:
                continue
            period = (event.timestamp - previous.timestamp).total_seconds() if previous else profile.period_mean
            previous = event
            period_z = _z(period, profile.period_mean, profile.period_std)
            payload_z = _z(float(event.payload_size or 0), profile.payload_mean, profile.payload_std)
            new_peer = bool(event.peer and event.peer not in profile.allowed_peers)
            new_command = bool(event.command and event.command not in profile.allowed_commands)
            off_window = bool(event.command and profile.maintenance_windows and not any(_in_window(event.timestamp.time(), a, b) for a, b in profile.maintenance_windows))
            rules = []
            if period_z >= threshold: rules.append("IOT-PERIOD-DEVIATION")
            if payload_z >= threshold: rules.append("IOT-PAYLOAD-DEVIATION")
            if new_peer: rules.append("IOT-NEW-PEER")
            if new_command: rules.append("IOT-UNAUTHORIZED-COMMAND")
            if off_window: rules.append("IOT-OFF-WINDOW-CONTROL")
            if rules:
                findings.append(DetectionFinding(
                    stable_id("find", "iot", event.event_id), event.event_id, rules[0],
                    "IoT behavioural deviation", "high" if off_window or new_command else "medium", Stage.IMPACT if off_window else Stage.DISCOVERY,
                    "; ".join(rules), {"period_z": round(period_z, 3), "payload_z": round(payload_z, 3), "new_peer": new_peer, "new_command": new_command, "off_window": off_window},
                ))
    return findings
