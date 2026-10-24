from time import perf_counter

from chainbreaker.web.app import process_rows
from chainbreaker.evaluation.metrics import correct_chain_rate, time_to_detect
from chainbreaker.evaluation.metrics import precision_recall_f1
try:
    from evaluation.scenario_suite import scenario_rows
except ModuleNotFoundError:
    from scenario_suite import scenario_rows


def benchmark() -> dict[str, float]:
    rows, expected, expected_stages = scenario_rows("spray-to-traffic-controller")
    tick = perf_counter()
    run = process_rows(rows, expected_attack_ids=expected, expected_stages=expected_stages, expected_cluster_labels={str(row["event_id"]): "central-incident" for row in rows})
    elapsed = perf_counter() - tick
    detected = {finding.event_id for finding in run["findings"]}
    pr = precision_recall_f1(expected, detected)
    return {
        "events": float(len(run["events"])),
        "findings": float(len(run["findings"])),
        "links": float(len(run["links"])),
        "chains": float(len(run["chains"])),
        "event_precision": round(pr["precision"], 4),
        "event_recall": round(pr["recall"], 4),
        "event_f1": round(pr["f1"], 4),
        "incident_ari": float(run["metrics"]["incident_ari"]),
        "correct_chain_rate": correct_chain_rate(run["chains"], expected_stages),
        "time_to_detect_seconds": time_to_detect(run["events"], run["findings"], expected),
        "events_per_second": len(run["events"]) / max(elapsed, 1e-9),
        "brier_score": float(run["calibration"].brier_score),
    }


if __name__ == "__main__":
    print(benchmark())
