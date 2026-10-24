from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, event_count INTEGER NOT NULL, incident_count INTEGER NOT NULL, merkle_root TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (run_id TEXT NOT NULL, event_id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY (run_id, event_id));
        CREATE TABLE IF NOT EXISTS findings (run_id TEXT NOT NULL, finding_id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY (run_id, finding_id));
        """)
