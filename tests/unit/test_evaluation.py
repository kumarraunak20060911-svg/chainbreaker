from chainbreaker.evaluation.metrics import adjusted_rand_index, precision_recall_f1


def test_evaluation_metrics_cover_detection_and_clustering():
    assert precision_recall_f1({"a", "b"}, {"a", "c"}) == {"precision": 0.5, "recall": 0.5, "f1": 0.5}
    assert adjusted_rand_index(("attack", "attack", "benign"), ("cluster-1", "cluster-1", "cluster-2")) == 1.0
