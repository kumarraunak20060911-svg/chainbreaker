from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import socket
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
        config_path = Path(path)
        if not config_path.is_file():
            fallback = Path(__file__).resolve().parent.parent.parent / "config" / "default.toml"
            if fallback.is_file():
                config_path = fallback
        data = tomllib.loads(config_path.read_text())
        storage = data.get("storage", {})
        analysis = data.get("analysis", {})
        security = data.get("security", {})
        project_root = Path(__file__).resolve().parent.parent.parent
        default_sqlite_test = f"sqlite+pysqlite:///{(project_root / 'runtime' / 'databases' / 'chainbreaker-test.sqlite3').as_posix()}"
        settings = cls(
            database_url=os.getenv("CHAINBREAKER_DATABASE_URL", storage.get("database_url", "postgresql+psycopg://chainbreaker:change-me@localhost:5432/chainbreaker")),
            sqlite_test_url=storage.get("sqlite_test_url", default_sqlite_test),
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
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def database_path(self) -> Path:
        """Path for local SQLite database."""
        path = self.project_root / "runtime" / "databases" / "chainbreaker.sqlite3"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def resolved_database_url(self) -> str:
        if self.environment == "test":
            return self.sqlite_test_url
        if "CHAINBREAKER_DATABASE_URL" in os.environ:
            return os.environ["CHAINBREAKER_DATABASE_URL"]
        # In development/default mode, check if PostgreSQL is actually listening on localhost
        if self.database_url.startswith("postgresql"):
            try:
                s = socket.socket()
                s.settimeout(0.2)
                reachable = s.connect_ex(("127.0.0.1", 5432)) == 0
                s.close()
                if reachable:
                    return self.database_url
            except Exception:
                pass
            return f"sqlite+pysqlite:///{self.database_path.as_posix()}"
        return self.database_url
