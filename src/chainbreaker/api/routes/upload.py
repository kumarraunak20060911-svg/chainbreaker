from __future__ import annotations

from pathlib import Path
import json
from uuid import uuid4

from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from chainbreaker.api.tenant import organization_id
from chainbreaker.ingest.jobs import submit_job
from chainbreaker.settings import Settings

router = APIRouter()


@router.post("/ingest", status_code=202)
async def ingest(file: UploadFile = File(...), assets_file: UploadFile | None = File(None), inventory_file: UploadFile | None = File(None), x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    settings = Settings.load()
    organization = organization_id(x_organization_id, x_user_id)
    if not file.filename or Path(file.filename).suffix.lower() not in {".csv", ".jsonl"}:
        raise HTTPException(415, "only CSV and JSONL files are supported")
    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(413, "upload exceeds configured size limit")
    safe_name = f"{uuid4().hex}-{Path(file.filename).name}"
    destination = settings.upload_directory / safe_name
    destination.write_bytes(content)
    asset_path = None
    inventory_path = None
    for uploaded, label in ((assets_file, "assets"), (inventory_file, "inventory")):
        if uploaded and uploaded.filename:
            supplemental = settings.upload_directory / f"{uuid4().hex}-{label}-{Path(uploaded.filename).name}"
            supplemental.write_bytes(await uploaded.read())
            if label == "assets":
                asset_path = str(supplemental)
            else:
                inventory_path = str(supplemental)
    try:
        from chainbreaker.storage.persistent import create_job, ensure_organization
        ensure_organization(organization, settings=settings)
        job_id = create_job(organization, json.dumps({"events": str(destination), "assets": asset_path, "inventory": inventory_path}), settings=settings)
    except Exception as exc:
        if settings.environment == "production":
            raise HTTPException(503, "persistent job storage is unavailable") from exc
        raise HTTPException(503, "database is unavailable; start PostgreSQL or use the test profile") from exc
    submit_job(job_id, organization, str(destination), settings=settings)
    return {"job_id": job_id, "status": "PENDING", "organization_id": organization, "dataset_reference": str(destination)}
