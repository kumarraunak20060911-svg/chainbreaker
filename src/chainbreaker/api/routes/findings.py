from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from chainbreaker.api.tenant import organization_id
from chainbreaker.settings import Settings
from chainbreaker.storage.persistent import list_findings

router = APIRouter()


@router.get("/findings")
def findings(limit: int = 100, offset: int = 0, severity: str | None = None, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    if not 0 <= offset <= 1_000_000 or not 1 <= limit <= 500:
        raise HTTPException(422, "invalid pagination")
    items = list_findings(organization_id(x_organization_id, x_user_id), limit=limit, offset=offset, severity=severity, settings=Settings.load())
    return {"items": [{"finding_id": item.id, "detection_type": item.detection_type, "severity": item.severity, "event_ids": item.event_ids, "evidence_details": item.evidence_details, "explanation": item.explanation, "created_at": item.created_at} for item in items], "limit": limit, "offset": offset}
