from chainbreaker.web.app import demo_run


def benchmark() -> dict[str, float]:
    run = demo_run()
    expected = {"evt-004", "evt-005", "evt-006", "evt-007"}
    detected = {finding.event_id for finding in run["findings"]}
    true_positive = len(expected & detected)
    precision = true_positive / len(detected) if detected else 0.0
    recall = true_positive / len(expected)
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {"events": float(len(run["events"])), "findings": float(len(run["findings"])), "links": float(len(run["links"])), "chains": float(len(run["chains"])), "event_precision": round(precision, 4), "event_recall": round(recall, 4), "event_f1": round(f1, 4), "brier_score": float(run["calibration"].brier_score)}


if __name__ == "__main__":
    print(benchmark())
