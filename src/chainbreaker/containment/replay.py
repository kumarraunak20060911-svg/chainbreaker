from __future__ import annotations

import networkx as nx


def replay_without(graph: nx.DiGraph, removed: str, sources: list[str], targets: list[str]) -> dict[str, object]:
    replay = graph.copy()
    if removed in replay:
        replay.remove_node(removed)
    residual = [(source, target) for source in sources for target in targets if source in replay and target in replay and nx.has_path(replay, source, target)]
    return {"removed": removed, "residual_paths": residual, "contained": not residual}
