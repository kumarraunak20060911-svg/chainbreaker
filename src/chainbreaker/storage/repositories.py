from __future__ import annotations

import json
from dataclasses import asdict

from .database import connect


def save_run(path, run_id, created_at, events, findings, merkle_root, incident_count=1):
    with connect(path) as connection:
        connection.execute("INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?)", (run_id, created_at, len(events), incident_count, merkle_root))
        connection.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?)", [(run_id, event.event_id, json.dumps(asdict(event), default=str)) for event in events])
        connection.executemany("INSERT OR REPLACE INTO findings VALUES (?, ?, ?)", [(run_id, finding.finding_id, json.dumps(asdict(finding), default=str)) for finding in findings])


def latest_run(path):
    with connect(path) as connection:
        return connection.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 1").fetchone()
