from __future__ import annotations

from fastapi import Header, HTTPException

from chainbreaker.settings import Settings


def organization_id(x_organization_id: str | None = Header(default=None), x_user_id: str | None = Header(default=None)) -> str:
    settings = Settings.load()
    if x_organization_id:
        return x_organization_id[:64]
    if settings.require_tenant_header and settings.environment == "production":
        if not x_organization_id or not x_user_id:
            raise HTTPException(status_code=401, detail="X-Organization-ID and X-User-ID are required")
        return x_organization_id[:64]
    return "dev-organization"
