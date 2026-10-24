from __future__ import annotations

import json
from dataclasses import asdict

from .database import connect


def save_run(path, run_id, created_at, events, findings, merkle_root, incident_count=1, links=(), report=None):
    with connect(path) as connection:
        connection.execute("INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?)", (run_id, created_at, len(events), incident_count, merkle_root))
        connection.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?)", [(run_id, event.event_id, json.dumps(asdict(event), default=str)) for event in events])
        connection.executemany("INSERT OR REPLACE INTO findings VALUES (?, ?, ?)", [(run_id, finding.finding_id, json.dumps(asdict(finding), default=str)) for finding in findings])
        connection.executemany("INSERT OR REPLACE INTO links VALUES (?, ?, ?)", [(run_id, link.link_id, json.dumps(asdict(link), default=str)) for link in links])
        if report is not None:
            connection.execute("INSERT OR REPLACE INTO reports VALUES (?, ?)", (run_id, json.dumps(report, default=str)))


def latest_run(path):
    with connect(path) as connection:
        return connection.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 1").fetchone()


def save_decision(path, run_id, decision_id, action_id, decision, actor, created_at, reason):
    with connect(path) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, decision_id, action_id, decision, actor, created_at, reason),
        )
