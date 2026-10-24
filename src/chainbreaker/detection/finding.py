from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from chainbreaker.domain.enums import Stage


@dataclass(frozen=True, slots=True)
class DetectionFinding:
    finding_id: str
    event_id: str
    rule_id: str
    title: str
    severity: str
    stage: Stage
    explanation: str
    features: dict[str, Any] = field(default_factory=dict)
