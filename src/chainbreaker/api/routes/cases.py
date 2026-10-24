from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from chainbreaker.api.tenant import organization_id
from chainbreaker.settings import Settings
from chainbreaker.storage.persistent import create_case, get_case, list_cases

router = APIRouter()


class CaseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


@router.post("/cases", status_code=201)
def create(request: CaseRequest, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    org = organization_id(x_organization_id, x_user_id)
    return {"case_id": create_case(org, request.title, request.description, request.priority, settings=Settings.load()), "organization_id": org}


@router.get("/cases")
def cases(limit: int = 100, offset: int = 0, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    if not 0 <= offset <= 1_000_000 or not 1 <= limit <= 500:
        raise HTTPException(422, "invalid pagination")
    return {"items": [{"case_id": item.id, "title": item.title, "description": item.description, "status": item.status, "priority": item.priority, "created_at": item.created_at, "updated_at": item.updated_at} for item in list_cases(organization_id(x_organization_id, x_user_id), limit=limit, offset=offset, settings=Settings.load())], "limit": limit, "offset": offset}


@router.get("/cases/{case_id}")
def case(case_id: str, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    item = get_case(case_id, organization_id(x_organization_id, x_user_id), settings=Settings.load())
    if item is None:
        raise HTTPException(404, "case not found")
    return {"case_id": item.id, "title": item.title, "description": item.description, "status": item.status, "priority": item.priority, "analyst_notes": item.analyst_notes, "disposition": item.disposition, "created_at": item.created_at, "updated_at": item.updated_at}
