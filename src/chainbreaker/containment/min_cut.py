from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import networkx as nx

from chainbreaker.domain.enums import ActionType, Criticality
from chainbreaker.domain.models import Asset, CandidateAction
from chainbreaker.domain.policies import action_allowed


@dataclass(frozen=True, slots=True)
class CutResult:
    nodes: tuple[str, ...]
    cost: float


def weighted_vertex_cut(graph: nx.DiGraph, sources: Iterable[str], targets: Iterable[str], assets: Mapping[str, Asset]) -> CutResult:
    split = nx.DiGraph()
    infinity = 1e12
    for node in graph.nodes:
        asset = assets.get(node)
        multiplier = 1000 if asset and asset.criticality is Criticality.LIFE_SAFETY else 100 if asset and asset.criticality is Criticality.ESSENTIAL else 1
        service_cost = max(1.0, float(len(asset.baseline_services) if asset else 1))
        split.add_edge((node, "in"), (node, "out"), capacity=multiplier * service_cost)
    for source, target, data in graph.edges(data=True):
        split.add_edge((source, "out"), (target, "in"), capacity=float(data.get("capacity", infinity)))
    super_source, super_target = ("source", "out"), ("target", "in")
    for source in sources: split.add_edge(super_source, (source, "in"), capacity=infinity)
    for target in targets: split.add_edge((target, "out"), super_target, capacity=infinity)
    _, (reachable, blocked) = nx.minimum_cut(split, super_source, super_target, capacity="capacity")
    nodes = tuple(sorted(node for node in graph.nodes if (node, "in") in reachable and (node, "out") in blocked))
    return CutResult(nodes, sum(split[(node, "in")][(node, "out")]["capacity"] for node in nodes))


def evaluate_action(action_id: str, action_type: ActionType, target: Asset, evidence_severed: float, *, affected_services: Iterable[str] = ()) -> CandidateAction:
    allowed = action_allowed(action_type, target.criticality)
    return CandidateAction(
        action_id=action_id,
        action_type=action_type,
        target_id=target.asset_id,
        evidence_severed=max(0.0, min(1.0, evidence_severed)),
        collateral_cost=(1000.0 if target.criticality is Criticality.LIFE_SAFETY else 100.0 if target.criticality is Criticality.ESSENTIAL else 1.0) * max(1, len(target.baseline_services)),
        criticality=target.criticality,
        auto_recommendable=allowed,
        reason="Life-safety isolation is prohibited; prefer a narrower control" if not allowed else "Human approval required before execution",
        affected_services=tuple(affected_services),
    )
