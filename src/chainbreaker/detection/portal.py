from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable
from collections import defaultdict

from chainbreaker.domain.enums import Stage
from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event

from .finding import DetectionFinding


def detect_portal(events: Iterable[Event], trusted_domains: Iterable[str] = ("city.example", "central.example")) -> list[DetectionFinding]:
    trusted = tuple(trusted_domains)
    findings = []
    by_host = defaultdict(list)
    for event in events:
        if event.host:
            by_host[event.host].append(event)
        domain = event.domain or ""
        similarity = max((SequenceMatcher(None, domain, known).ratio() for known in trusted), default=0.0)
        suspicious_url = any(token in (event.metadata.get("url", "") or "") for token in ("%2f", "../", "base64", "cmd="))
        if 0.65 <= similarity < 1.0 or suspicious_url:
            findings.append(DetectionFinding(
                stable_id("find", "portal", event.event_id), event.event_id, "PORTAL-LOOKALIKE-OR-URL",
                "Portal URL indicator", "medium", Stage.INITIAL_ACCESS,
                "URL resembles a trusted city domain or contains an encoded/traversal indicator",
                {"similarity": round(similarity, 3), "suspicious_url": suspicious_url},
            ))
    for host, items in by_host.items():
        ordered = sorted(items, key=lambda item: item.timestamp)
        for index, event in enumerate(ordered):
            window_start = event.timestamp.timestamp() - 300
            count = sum(window_start <= candidate.timestamp.timestamp() <= event.timestamp.timestamp() for candidate in ordered[: index + 1])
            if count >= 8:
                findings.append(DetectionFinding(
                    stable_id("find", "portal-burst", host, event.event_id), event.event_id, "PORTAL-HOST-BURST",
                    "Portal request burst", "medium", Stage.INITIAL_ACCESS,
                    "A single host generated an unusual number of portal events in a five-minute window",
                    {"host": host, "five_minute_count": count},
                ))
    return findings
