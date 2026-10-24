from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from heapq import nlargest
from math import log
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class StageNode:
    node_id: str
    timestamp: datetime
    stage_tag: str
    row_ids: tuple[str, ...] = ()
    technique_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StageEdge:
    edge_id: str
    source: str
    target: str
    weight: float
    row_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Justification:
    row_ids: tuple[str, ...]
    complete: bool
    method: str = "greedy-set-cover"
    row_count: int = 0


@dataclass(frozen=True, slots=True)
class AttackChain:
    score: float
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    stage_tags: tuple[str, ...]
    justification: Justification


def infer_top_k(nodes: Iterable[StageNode], edges: Iterable[StageEdge], transition_probabilities: Mapping[str, Mapping[str, float]], *, top_k: int = 3) -> list[AttackChain]:
    node_list = sorted(nodes, key=lambda node: (node.timestamp, node.node_id))
    edge_list = list(edges)
    by_id = {node.node_id: node for node in node_list}
    incoming: dict[str, list[StageEdge]] = {node.node_id: [] for node in node_list}
    outgoing: dict[str, list[StageEdge]] = {node.node_id: [] for node in node_list}
    for edge in edge_list:
        if edge.source not in by_id or edge.target not in by_id or by_id[edge.source].timestamp >= by_id[edge.target].timestamp:
            raise ValueError("edges must form a forward-only temporal DAG")
        incoming[edge.target].append(edge)
        outgoing[edge.source].append(edge)
    paths: dict[str, list[tuple[float, tuple[str, ...], tuple[str, ...]]]] = {}
    for node in node_list:
        candidates: list[tuple[float, tuple[str, ...], tuple[str, ...]]] = [(0.0, (node.node_id,), ())]
        for edge in incoming[node.node_id]:
            for score, node_ids, edge_ids in paths.get(edge.source, []):
                p = transition_probabilities.get(by_id[edge.source].stage_tag, {}).get(node.stage_tag, 0.05)
                candidates.append((score + edge.weight + log(max(p, 1e-12)), node_ids + (node.node_id,), edge_ids + (edge.edge_id,)))
        paths[node.node_id] = nlargest(top_k, candidates, key=lambda item: (item[0], item[1]))
    terminals = [item for node in node_list if not outgoing[node.node_id] for item in paths[node.node_id]]
    multi_stage = [item for item in terminals if len(item[1]) >= 2]
    ranked = multi_stage or terminals
    best = nlargest(top_k, ranked, key=lambda item: (item[0], len(item[1]), item[1]))
    edges_by_id = {edge.edge_id: edge for edge in edge_list}
    result = []
    for score, node_ids, edge_ids in best:
        justification = minimal_justification(node_ids, edge_ids, by_id, edges_by_id)
        result.append(AttackChain(score, node_ids, edge_ids, tuple(by_id[node_id].stage_tag for node_id in node_ids), justification))
    return result


def minimal_justification(
    node_ids: tuple[str, ...],
    edge_ids: tuple[str, ...],
    nodes: Mapping[str, StageNode],
    edges: Mapping[str, StageEdge],
) -> Justification:
    """Select the smallest greedy row set covering every chain node and transition."""
    units: dict[str, set[str]] = {}
    for index, node_id in enumerate(node_ids):
        rows = set(nodes[node_id].row_ids or (node_id,))
        units[f"node:{index}"] = rows
    for index, edge_id in enumerate(edge_ids):
        rows = set(edges[edge_id].row_ids or (edge_id,))
        units[f"edge:{index}"] = rows
    candidates = sorted({row for rows in units.values() for row in rows})
    uncovered = set(units)
    selected: list[str] = []
    while uncovered:
        best = max(candidates, key=lambda row: (sum(row in units[unit] for unit in uncovered), row), default=None)
        if best is None or not any(best in units[unit] for unit in uncovered):
            break
        selected.append(best)
        uncovered = {unit for unit in uncovered if best not in units[unit]}
        candidates.remove(best)
    return Justification(tuple(sorted(selected)), not uncovered, "greedy-set-cover", len(selected))


class StageAwareViterbi:
    def __init__(self, transition_probabilities: Mapping[str, Mapping[str, float]] | None = None) -> None:
        self.transitions = transition_probabilities or {}

    def infer(self, nodes: Iterable[StageNode], edges: Iterable[StageEdge], *, top_k: int = 3) -> list[AttackChain]:
        return infer_top_k(nodes, edges, self.transitions, top_k=top_k)
