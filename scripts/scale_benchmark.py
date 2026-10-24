from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
import tracemalloc
from datetime import datetime, timedelta, timezone
from pathlib import Path

from chainbreaker.ingest.service import ingest_rows_diagnostics


def synthetic_rows(count: int):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for index in range(count):
        yield {"event_id": f"scale-{index}", "row_id": f"row-{index}", "timestamp": (start + timedelta(seconds=index)).isoformat(), "source": "auth" if index % 2 else "dns", "event_type": "login_success" if index % 2 else "dns_query", "account": f"user-{index % 1000}", "ip": f"198.51.100.{index % 250}", "domain": f"host-{index % 500}.example.org" if index % 2 == 0 else "", "success": "true" if index % 2 else ""}


def run(count: int) -> dict[str, object]:
    tracemalloc.start()
    started = time.perf_counter()
    accepted, diagnostics = ingest_rows_diagnostics(synthetic_rows(count))
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {"events_requested": count, "events_accepted": len(accepted), "events_rejected": len(diagnostics.rejected_rows), "elapsed_seconds": round(elapsed, 6), "events_per_second": round(count / max(elapsed, 1e-9), 2), "peak_memory_bytes": peak, "python": sys.version, "platform": platform.platform()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=int, nargs="+", default=[10_000, 100_000])
    parser.add_argument("--output", type=Path, default=Path("runtime/benchmarks/scale.json"))
    args = parser.parse_args()
    results = [run(count) for count in args.events]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2))
    print(json.dumps(results, indent=2))
