from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    sqlite_test_url: str
    upload_directory: Path
    report_directory: Path
    top_k_chains: int = 3
    minimum_link_probability: float = 0.55
    batch_size: int = 500
    job_poll_seconds: float = 0.5
    analysis_window_events: int = 50000
    environment: str = "development"
    require_tenant_header: bool = False
    max_upload_bytes: int = 104857600
    retention_days: int = 90

    @classmethod
    def load(cls, path: str | Path = "config/default.toml") -> "Settings":
        data = tomllib.loads(Path(path).read_text())
        storage = data.get("storage", {})
        analysis = data.get("analysis", {})
        security = data.get("security", {})
        settings = cls(
            database_url=os.getenv("CHAINBREAKER_DATABASE_URL", storage.get("database_url", "postgresql+psycopg://chainbreaker:change-me@localhost:5432/chainbreaker")),
            sqlite_test_url=storage.get("sqlite_test_url", "sqlite+pysqlite:///runtime/databases/chainbreaker-test.sqlite3"),
            upload_directory=Path(storage.get("upload_directory", "runtime/uploads")),
            report_directory=Path(storage.get("report_directory", "runtime/reports")),
            top_k_chains=int(analysis.get("top_k_chains", 3)),
            minimum_link_probability=float(analysis.get("minimum_link_probability", 0.55)),
            batch_size=int(storage.get("batch_size", 500)),
            job_poll_seconds=float(storage.get("job_poll_seconds", 0.5)),
            analysis_window_events=int(storage.get("analysis_window_events", 50000)),
            environment=os.getenv("CHAINBREAKER_ENVIRONMENT", security.get("environment", "development")),
            require_tenant_header=bool(security.get("require_tenant_header", False)),
            max_upload_bytes=int(security.get("max_upload_bytes", 104857600)),
            retention_days=int(security.get("retention_days", 90)),
        )
        settings.upload_directory.mkdir(parents=True, exist_ok=True)
        settings.report_directory.mkdir(parents=True, exist_ok=True)
        return settings

    @property
    def database_path(self) -> Path:
        """Compatibility path for legacy local report tooling."""
        return Path("runtime/databases/chainbreaker.sqlite3")

    def resolved_database_url(self) -> str:
        if self.environment == "test":
            return self.sqlite_test_url
        return self.database_url
