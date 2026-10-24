from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from typing import Iterable

from chainbreaker.domain.enums import Stage
from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event

from .finding import DetectionFinding


def detect_auth(events: Iterable[Event]) -> list[DetectionFinding]:
    auth = [event for event in events if event.source.value in {"auth", "vpn"}]
    by_ip: defaultdict[str, list[Event]] = defaultdict(list)
    for event in auth:
        if event.ip:
            by_ip[event.ip].append(event)
    findings: list[DetectionFinding] = []
    for ip, items in by_ip.items():
        failures = [item for item in items if item.success is False or "fail" in item.event_type.lower()]
        accounts = {item.account for item in items if item.account}
        if len(failures) >= 3 and len(accounts) >= 2:
            for event in failures:
                findings.append(DetectionFinding(
                    stable_id("find", "spray", event.event_id), event.event_id, "AUTH-SPRAY",
                    "Password-spray pattern", "high", Stage.CREDENTIAL_ACCESS,
                    f"{len(failures)} failures against {len(accounts)} accounts from one source",
                    {"source_ip": ip, "failures": len(failures), "distinct_accounts": len(accounts)},
                ))
    ordered = sorted(auth, key=lambda item: item.timestamp)
    for left, right in zip(ordered, ordered[1:]):
        if left.account and right.account == left.account and left.success is False and right.success is True and right.timestamp - left.timestamp <= timedelta(minutes=10):
            findings.append(DetectionFinding(
                stable_id("find", "success-after-fail", right.event_id), right.event_id, "AUTH-FAILURES-THEN-SUCCESS",
                "Failures followed by valid login", "high", Stage.INITIAL_ACCESS,
                "A valid login followed a recent failed sequence for the same account",
                {"failed_event_id": left.event_id},
            ))
    return findings
