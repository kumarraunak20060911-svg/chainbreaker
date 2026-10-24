from __future__ import annotations

from chainbreaker.domain.enums import ActionType
from chainbreaker.domain.models import Asset, CandidateAction
import networkx as nx

from .min_cut import evaluate_action, weighted_vertex_cut
from .pareto import ParetoPlan, build_pareto_frontier


def plan_actions(target: Asset, *, primary_severance: float = .82, graph: nx.DiGraph | None = None, source_nodes: tuple[str, ...] = ("operator",), target_nodes: tuple[str, ...] | None = None) -> ParetoPlan:
    analysis_graph = graph or nx.DiGraph([("operator", target.asset_id)])
    analysis_graph.add_node(target.asset_id)
    cut = weighted_vertex_cut(analysis_graph, source_nodes, target_nodes or (target.asset_id,), {target.asset_id: target})
    cut_adjustment = min(0.08, 0.01 * len(cut.nodes))
    actions = [
        evaluate_action("revoke-session", ActionType.REVOKE_SESSION, target, min(1.0, primary_severance + cut_adjustment), affected_services=target.baseline_services),
        evaluate_action("block-command", ActionType.BLOCK_COMMAND, target, max(.55, primary_severance - .1 + cut_adjustment), affected_services=("unauthorized command",)),
        evaluate_action("isolate-host", ActionType.ISOLATE_HOST, target, min(1.0, primary_severance + .08 + cut_adjustment), affected_services=target.baseline_services),
    ]
    return build_pareto_frontier(actions)
