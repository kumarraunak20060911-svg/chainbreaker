import networkx as nx
from chainbreaker.containment.replay import replay_without


def test_counterfactual_replay_contains_attack():
    graph = nx.DiGraph()
    graph.add_edge("actor", "ops_session")
    graph.add_edge("ops_session", "gateway_gw3")
    graph.add_edge("gateway_gw3", "traffic_controller_tc14")

    # When ops_session is severed (Cut A)
    result = replay_without(graph, "ops_session", ["actor"], ["traffic_controller_tc14"])
    assert result["contained"] is True
    assert len(result["residual_paths"]) == 0

    # When an unrelated node is removed, attack remains uncontained
    unrelated = replay_without(graph, "unrelated_node", ["actor"], ["traffic_controller_tc14"])
    assert unrelated["contained"] is False
    assert len(unrelated["residual_paths"]) > 0
