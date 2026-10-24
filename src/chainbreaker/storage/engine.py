from __future__ import annotations

from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from chainbreaker.settings import Settings
from .models import Base


@lru_cache(maxsize=4)
def get_engine(database_url: str) -> Engine:
    kwargs: dict[str, object] = {"pool_pre_ping": True, "future": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs.update({"pool_size": 5, "max_overflow": 10, "pool_timeout": 30})
    return create_engine(database_url, **kwargs)


def session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    current = settings or Settings.load()
    if current.environment == "test":
        initialize_schema(current)
    return sessionmaker(bind=get_engine(current.resolved_database_url()), expire_on_commit=False, autoflush=False)


def dependency_health(settings: Settings | None = None) -> dict[str, object]:
    current = settings or Settings.load()
    try:
        with get_engine(current.resolved_database_url()).connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable", "backend": current.resolved_database_url().split(":", 1)[0]}
    except Exception as exc:
        return {"status": "degraded", "database": "unreachable", "backend": current.resolved_database_url().split(":", 1)[0], "error_type": type(exc).__name__}


def initialize_schema(settings: Settings | None = None) -> None:
    current = settings or Settings.load()
    if current.environment == "test":
        Base.metadata.create_all(get_engine(current.resolved_database_url()))
