from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from chainbreaker.api.tenant import organization_id
from chainbreaker.settings import Settings
from chainbreaker.storage.persistent import list_events

router = APIRouter()


@router.get("/events")
def events(limit: int = 100, offset: int = 0, source_id: str | None = None, x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)):
    if not 0 <= offset <= 1_000_000 or not 1 <= limit <= 500:
        raise HTTPException(422, "invalid pagination")
    items = list_events(organization_id(x_organization_id, x_user_id), limit=limit, offset=offset, source_id=source_id, settings=Settings.load())
    return {"items": [{"event_id": item.id, "timestamp": item.event_timestamp, "event_type": item.event_type, "account_ref": item.account_ref, "host_ref": item.host_ref, "ip_ref": item.ip_ref, "device_ref": item.device_ref, "attributes": item.attributes, "provenance": {"source": item.provenance.get("source"), "pseudonymized": item.provenance.get("pseudonymized")}} for item in items], "limit": limit, "offset": offset}
