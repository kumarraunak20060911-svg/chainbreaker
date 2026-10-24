from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from math import log
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
            posterior_failure_rate = (len(failures) + 1) / (len(items) + 2)
            for event in failures:
                findings.append(DetectionFinding(
                    stable_id("find", "spray", event.event_id), event.event_id, "AUTH-SPRAY",
                    "Password-spray pattern", "high", Stage.CREDENTIAL_ACCESS,
                    f"{len(failures)} failures against {len(accounts)} accounts from one source",
                    {"source_ip": ip, "failures": len(failures), "distinct_accounts": len(accounts), "beta_binomial_posterior_failure_rate": round(posterior_failure_rate, 4)},
                ))
            if posterior_failure_rate >= 0.6:
                findings.append(DetectionFinding(
                    stable_id("find", "beta-binomial", ip), failures[-1].event_id, "AUTH-BETA-BINOMIAL",
                    "Elevated source failure rate", "medium", Stage.CREDENTIAL_ACCESS,
                    "Beta(1,1) posterior mean indicates an unusually high failure rate for this source",
                    {"source_ip": ip, "posterior_failure_rate": round(posterior_failure_rate, 4)},
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
    cusum = 0.0
    for event in ordered:
        failure = event.success is False or "fail" in event.event_type.lower()
        cusum = max(0.0, cusum + (0.8 if failure else -0.2))
        if cusum >= 2.4:
            findings.append(DetectionFinding(
                stable_id("find", "cusum", event.event_id), event.event_id, "AUTH-CUSUM-LOW-SLOW",
                "Low-and-slow authentication pressure", "medium", Stage.CREDENTIAL_ACCESS,
                "CUSUM accumulated repeated failures without requiring a burst threshold",
                {"cusum": round(cusum, 3)},
            ))
            cusum = 0.0
    return findings
