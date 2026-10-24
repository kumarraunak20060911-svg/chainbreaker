from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True, slots=True)
class Settings:
    database_path: Path
    upload_directory: Path
    report_directory: Path
    top_k_chains: int = 3
    minimum_link_probability: float = 0.55

    @classmethod
    def load(cls, path: str | Path = "config/default.toml") -> "Settings":
        data = tomllib.loads(Path(path).read_text())
        storage = data.get("storage", {})
        analysis = data.get("analysis", {})
        settings = cls(
            database_path=Path(storage.get("database_path", "runtime/databases/chainbreaker.sqlite3")),
            upload_directory=Path(storage.get("upload_directory", "runtime/uploads")),
            report_directory=Path(storage.get("report_directory", "runtime/reports")),
            top_k_chains=int(analysis.get("top_k_chains", 3)),
            minimum_link_probability=float(analysis.get("minimum_link_probability", 0.55)),
        )
        settings.database_path.parent.mkdir(parents=True, exist_ok=True)
        settings.upload_directory.mkdir(parents=True, exist_ok=True)
        settings.report_directory.mkdir(parents=True, exist_ok=True)
        return settings
