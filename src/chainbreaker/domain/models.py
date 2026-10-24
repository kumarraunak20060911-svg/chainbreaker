from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import ActionType, Criticality, EventSource, Stage


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    timestamp: datetime
    source: EventSource
    event_type: str
    account: str | None = None
    host: str | None = None
    ip: str | None = None
    device_id: str | None = None
    device_class: str | None = None
    peer: str | None = None
    domain: str | None = None
    command: str | None = None
    topic: str | None = None
    session_id: str | None = None
    payload_size: int | None = None
    success: bool | None = None
    row_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Asset:
    asset_id: str
    name: str
    asset_type: str
    criticality: Criticality
    baseline_services: tuple[str, ...] = ()
    owner: str = ""


@dataclass(frozen=True, slots=True)
class Finding:
    finding_id: str
    rule_id: str
    event_id: str
    severity: str
    title: str
    explanation: str
    features: dict[str, Any] = field(default_factory=dict)
    stage: Stage = Stage.DISCOVERY


@dataclass(frozen=True, slots=True)
class EvidenceLink:
    link_id: str
    left_event_id: str
    right_event_id: str
    entity_type: str
    entity_value: str
    weight: float
    probability: float
    explanation: str
    row_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Incident:
    incident_id: str
    title: str
    severity: str
    event_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    link_ids: tuple[str, ...]
    stages: tuple[Stage, ...]
    summary: str


@dataclass(frozen=True, slots=True)
class CandidateAction:
    action_id: str
    action_type: ActionType
    target_id: str
    evidence_severed: float
    collateral_cost: float
    criticality: Criticality
    auto_recommendable: bool
    reason: str
    affected_services: tuple[str, ...] = ()
