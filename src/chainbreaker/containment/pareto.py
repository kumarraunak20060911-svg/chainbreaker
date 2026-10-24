from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from chainbreaker.domain.models import CandidateAction


@dataclass(frozen=True, slots=True)
class ParetoPlan:
    frontier: tuple[CandidateAction, ...]
    recommended_action_id: str | None


def dominates(left: CandidateAction, right: CandidateAction) -> bool:
    return left.evidence_severed >= right.evidence_severed and left.collateral_cost <= right.collateral_cost and (left.evidence_severed > right.evidence_severed or left.collateral_cost < right.collateral_cost)


def build_pareto_frontier(actions: Iterable[CandidateAction]) -> ParetoPlan:
    items = list(actions)
    frontier = tuple(sorted((item for item in items if not any(dominates(other, item) for other in items if other.action_id != item.action_id)), key=lambda item: (-item.evidence_severed, item.collateral_cost)))
    safe = [item for item in frontier if item.auto_recommendable]
    recommended = min(safe, key=lambda item: (item.collateral_cost / max(item.evidence_severed, 1e-9), -item.evidence_severed), default=None)
    return ParetoPlan(frontier, recommended.action_id if recommended else None)
