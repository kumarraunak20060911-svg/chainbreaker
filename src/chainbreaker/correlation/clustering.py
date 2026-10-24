from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from chainbreaker.detection.finding import DetectionFinding
from chainbreaker.domain.models import EvidenceLink, Event


def cluster_findings(findings: Iterable[DetectionFinding]) -> list[tuple[str, ...]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for finding in findings:
        groups[finding.stage.value].append(finding.finding_id)
    return [tuple(items) for items in groups.values()]


def cluster_incidents(events: Iterable[Event], findings: Iterable[DetectionFinding], links: Iterable[EvidenceLink]) -> list[dict[str, tuple[str, ...]]]:
    """Cluster event evidence by linked entities and attach findings to each component."""
    event_ids = {event.event_id for event in events}
    parent = {event_id: event_id for event_id in event_ids}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(left: str, right: str) -> None:
        if left in parent and right in parent:
            root_left, root_right = find(left), find(right)
            if root_left != root_right:
                parent[root_right] = root_left

    for link in links:
        union(link.left_event_id, link.right_event_id)
    finding_map: defaultdict[str, list[str]] = defaultdict(list)
    for finding in findings:
        if finding.event_id in parent:
            finding_map[find(finding.event_id)].append(finding.finding_id)
    event_map: defaultdict[str, list[str]] = defaultdict(list)
    for event_id in event_ids:
        event_map[find(event_id)].append(event_id)
    return [
        {"event_ids": tuple(sorted(event_map[root])), "finding_ids": tuple(sorted(finding_map.get(root, [])))}
        for root in sorted(event_map)
    ]
