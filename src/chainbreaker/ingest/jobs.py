from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any
import json
from threading import Lock

from chainbreaker.ingest.service import ingest_rows_diagnostics, iter_rows
from chainbreaker.settings import Settings

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="chainbreaker-ingest")
_futures: dict[str, Future[object]] = {}
_lock = Lock()


def submit_job(job_id: str, organization_id: str, dataset_path: str, *, settings: Settings | None = None) -> None:
    from chainbreaker.web.app import process_rows

    current = settings or Settings.load()

    def run() -> object:
        from chainbreaker.storage.persistent import claim_job, persist_events, update_job
        if not claim_job(job_id, organization_id, settings=current):
            return None
        try:
            reference = json.loads(dataset_path) if dataset_path.lstrip().startswith("{") else {"events": dataset_path}
            events_path = Path(reference["events"])
            asset_rows = list(iter_rows(Path(reference["assets"]))) if reference.get("assets") else None
            inventory_rows = list(iter_rows(Path(reference["inventory"]))) if reference.get("inventory") else None
            analysis_rows: list[dict[str, Any]] = []
            processed = accepted = rejected = duplicates = 0
            batch: list[dict[str, Any]] = []
            file_size = max(events_path.stat().st_size, 1)
            bytes_seen = 0
            for row in iter_rows(events_path):
                batch.append(row)
                if len(batch) < current.batch_size:
                    continue
                parsed, diagnostics = ingest_rows_diagnostics(batch)
                if len(analysis_rows) < current.analysis_window_events:
                    analysis_rows.extend(batch[: current.analysis_window_events - len(analysis_rows)])
                accepted_count, duplicate_count = persist_events(parsed, organization_id, job_id, settings=current)
                processed += len(batch); accepted += accepted_count; rejected += len(diagnostics.rejected_rows); duplicates += duplicate_count
                bytes_seen = min(file_size, bytes_seen + sum(len(str(item)) for item in batch))
                update_job(job_id, organization_id, processed=processed, accepted=accepted, rejected=rejected, duplicates=duplicates, progress=min(0.9, bytes_seen / file_size), settings=current)
                batch = []
            if batch:
                parsed, diagnostics = ingest_rows_diagnostics(batch)
                if len(analysis_rows) < current.analysis_window_events:
                    analysis_rows.extend(batch[: current.analysis_window_events - len(analysis_rows)])
                accepted_count, duplicate_count = persist_events(parsed, organization_id, job_id, settings=current)
                processed += len(batch); accepted += accepted_count; rejected += len(diagnostics.rejected_rows); duplicates += duplicate_count
            result = process_rows(analysis_rows, organization_id=organization_id, ingestion_job_id=job_id, settings=current, asset_rows=asset_rows, inventory_rows=inventory_rows, persist=False)
            from chainbreaker.storage.persistent import persist_findings, save_report
            persist_findings(result["findings"], organization_id, settings=current)
            save_report(result["run_id"], organization_id, result["report"], settings=current)
            update_job(job_id, organization_id, status="SUCCEEDED", processed=processed, accepted=accepted, rejected=rejected, duplicates=duplicates, progress=1.0, settings=current)
            return result
        except Exception as exc:
            update_job(job_id, organization_id, status="FAILED", error_summary={"error_type": type(exc).__name__}, settings=current)
            raise

    with _lock:
        _futures[job_id] = _executor.submit(run)


def recover_pending_jobs(*, settings: Settings | None = None) -> int:
    current = settings or Settings.load()
    from chainbreaker.storage.persistent import list_jobs, recover_expired_jobs
    recover_expired_jobs("dev-organization", settings=current)
    jobs = list_jobs("dev-organization", settings=current)
    count = 0
    for job in jobs:
        reference = json.loads(job.input_dataset_reference) if job.input_dataset_reference.lstrip().startswith("{") else {"events": job.input_dataset_reference}
        if job.status in {"PENDING", "RETRYING"} and Path(reference["events"]).exists():
            submit_job(job.id, job.organization_id, job.input_dataset_reference, settings=current)
            count += 1
    return count
