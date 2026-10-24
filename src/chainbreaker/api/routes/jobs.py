from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Header, HTTPException

from chainbreaker.api.tenant import organization_id
from chainbreaker.settings import Settings
from chainbreaker.storage.persistent import get_job, list_jobs

router = APIRouter()


def _job_payload(job):
    return {"job_id": job.id, "organization_id": job.organization_id, "status": job.status, "dataset_reference": Path(job.input_dataset_reference).name, "created_at": job.created_at, "started_at": job.started_at, "completed_at": job.completed_at, "processed_events": job.processed_events, "accepted_events": job.accepted_events, "rejected_events": job.rejected_events, "duplicate_events": job.duplicate_events, "retry_count": job.retry_count, "progress": job.progress, "error_summary": job.error_summary}


from pathlib import Path


@router.get("/jobs")
def jobs(limit: int = 50, offset: int = 0, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    if not 0 <= offset <= 1_000_000 or not 1 <= limit <= 500:
        raise HTTPException(422, "invalid pagination")
    organization = organization_id(x_organization_id, x_user_id)
    return {"items": [_job_payload(job) for job in list_jobs(organization, limit=limit, offset=offset, settings=Settings.load())], "limit": limit, "offset": offset}


@router.get("/jobs/{job_id}")
def job(job_id: str, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    item = get_job(job_id, organization_id(x_organization_id, x_user_id), settings=Settings.load())
    if item is None:
        raise HTTPException(404, "job not found")
    return _job_payload(item)
