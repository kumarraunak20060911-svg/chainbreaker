from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from chainbreaker.detection.finding import DetectionFinding


def cluster_findings(findings: Iterable[DetectionFinding]) -> list[tuple[str, ...]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for finding in findings:
        groups[finding.stage.value].append(finding.finding_id)
    return [tuple(items) for items in groups.values()]
