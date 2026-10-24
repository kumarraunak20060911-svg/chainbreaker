from __future__ import annotations

import re
from typing import Iterable
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset, Event


def auto_discover_asset(
    device_id: str,
    *,
    host: str | None = None,
    command: str | None = None,
    topic: str | None = None,
    device_class: str | None = None,
) -> Asset:
    """Autonomously discover and classify untagged smart city assets from active telemetry.
    Solves the cold-start problem by protecting critical OT infrastructure even when
    the static inventory is incomplete or absent.
    """
    signature = f"{device_id} {host or ''} {command or ''} {topic or ''} {device_class or ''}".lower()

    # 1. Life-Safety Physical Infrastructure Patterns
    if any(k in signature for k in ("tc-", "traffic", "signal", "set-phase", "emergency-preempt", "preemption", "intersection")):
        return Asset(
            asset_id=device_id,
            name=f"Traffic Controller {device_id} (Auto-Discovered)",
            asset_type="signal-controller",
            criticality=Criticality.LIFE_SAFETY,
            baseline_services=("signal-phase", "emergency-preemption", "pedestrian-crossing"),
            owner="Municipal Department of Transportation",
        )

    if any(k in signature for k in ("water", "pump", "chlorine", "reservoir", "psi-override", "scada-water", "flow-valve")):
        return Asset(
            asset_id=device_id,
            name=f"Municipal Water RTU {device_id} (Auto-Discovered)",
            asset_type="water-pump-rtu",
            criticality=Criticality.LIFE_SAFETY,
            baseline_services=("potable-distribution", "pressure-regulation", "chlorine-monitoring"),
            owner="City Water & Waste Authority",
        )

    if any(k in signature for k in ("substation", "grid", "transformer", "feeder", "breaker", "trip-breaker", "350kw")):
        return Asset(
            asset_id=device_id,
            name=f"Power Substation Controller {device_id} (Auto-Discovered)",
            asset_type="substation-manager",
            criticality=Criticality.LIFE_SAFETY,
            baseline_services=("voltage-stabilization", "breaker-protection", "feeder-routing"),
            owner="Municipal Power & Light",
        )

    # 2. Essential Public Services Patterns
    if any(k in signature for k in ("ev-", "charger", "start-charge", "max-draw", "ocpp")):
        return Asset(
            asset_id=device_id,
            name=f"Fast Charger Manager {device_id} (Auto-Discovered)",
            asset_type="ev-charger",
            criticality=Criticality.ESSENTIAL,
            baseline_services=("power-metering", "session-auth", "load-balancing"),
            owner="Clean Transit Authority",
        )

    if any(k in signature for k in ("cam", "cctv", "rtsp", "surveillance", "badge", "cleanroom", "turnstile")):
        return Asset(
            asset_id=device_id,
            name=f"Security Sensor {device_id} (Auto-Discovered)",
            asset_type="camera",
            criticality=Criticality.ESSENTIAL,
            baseline_services=("perimeter-surveillance", "access-logging"),
            owner="Campus Public Safety",
        )

    # 3. Convenience / Standard Edge Devices
    return Asset(
        asset_id=device_id,
        name=f"Municipal IoT Node {device_id}",
        asset_type="iot-sensor",
        criticality=Criticality.CONVENIENCE,
        baseline_services=("telemetry-reporting",),
        owner="Smart City Operations",
    )


def enrich_inventory_with_discovery(
    known_assets: dict[str, Asset],
    events: Iterable[Event],
) -> dict[str, Asset]:
    """Inspect all active telemetry events and auto-populate missing asset records."""
    enriched = dict(known_assets)
    for event in events:
        dev_id = event.device_id or event.host
        if dev_id and dev_id not in enriched:
            enriched[dev_id] = auto_discover_asset(
                dev_id,
                host=event.host,
                command=event.command,
                topic=event.topic,
                device_class=event.device_class,
            )
    return enriched
