from datetime import datetime, timedelta, timezone

from chainbreaker.inference.viterbi import StageAwareViterbi, StageEdge, StageNode


def test_stage_aware_chain_returns_ordered_path():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    nodes = [StageNode("a", base, "credential-access", ("r1",)), StageNode("b", base + timedelta(seconds=1), "initial-access", ("r2",)), StageNode("c", base + timedelta(seconds=2), "impact", ("r3",))]
    edges = [StageEdge("ab", "a", "b", 3, ("r1", "r2")), StageEdge("bc", "b", "c", 4, ("r2", "r3"))]
    chains = StageAwareViterbi({"credential-access": {"initial-access": .9}, "initial-access": {"impact": .9}}).infer(nodes, edges)
    assert chains[0].node_ids == ("a", "b", "c")
