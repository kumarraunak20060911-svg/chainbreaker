from __future__ import annotations

import networkx as nx


def replay_without(graph: nx.DiGraph, removed: str, sources: list[str], targets: list[str]) -> dict[str, object]:
    replay = graph.copy()
    if removed in replay:
        replay.remove_node(removed)
    alternate_targets = [node for node in replay.nodes if replay.out_degree(node) == 0 and node not in targets]
    destinations = [target for target in targets if target in replay] + alternate_targets
    residual = [(source, target) for source in sources for target in destinations if source in replay and target in replay and nx.has_path(replay, source, target)]
    return {"removed": removed, "residual_paths": residual, "alternate_targets": alternate_targets, "contained": not residual}
