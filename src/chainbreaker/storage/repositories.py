from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .database import connect, initialize


def save_run(path, run_id, created_at, events, findings, merkle_root, incident_count=1, links=(), report=None):
    initialize(path)
    with connect(path) as connection:
        connection.execute("INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?)", (run_id, created_at, len(events), incident_count, merkle_root))
        connection.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?)", [(run_id, event.event_id, json.dumps(asdict(event), default=str)) for event in events])
        connection.executemany("INSERT OR REPLACE INTO findings VALUES (?, ?, ?)", [(run_id, finding.finding_id, json.dumps(asdict(finding), default=str)) for finding in findings])
        connection.executemany("INSERT OR REPLACE INTO links VALUES (?, ?, ?)", [(run_id, link.link_id, json.dumps(asdict(link), default=str)) for link in links])
        if report is not None:
            connection.execute("INSERT OR REPLACE INTO reports VALUES (?, ?)", (run_id, json.dumps(report, default=str)))


def latest_run(path):
    initialize(path)
    with connect(path) as connection:
        return connection.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 1").fetchone()


def list_runs(path) -> list[dict[str, Any]]:
    initialize(path)
    with connect(path) as connection:
        rows = connection.execute("SELECT run_id, created_at, event_count, incident_count, merkle_root FROM runs ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_run(path, run_id: str) -> dict[str, Any] | None:
    initialize(path)
    with connect(path) as connection:
        run_row = connection.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if not run_row:
            return None
        report_row = connection.execute("SELECT payload FROM reports WHERE run_id = ?", (run_id,)).fetchone()
        report = json.loads(report_row["payload"]) if report_row else None
        decisions = [dict(row) for row in connection.execute("SELECT * FROM decisions WHERE run_id = ? ORDER BY created_at DESC", (run_id,)).fetchall()]
        return {
            "run_id": run_row["run_id"],
            "created_at": run_row["created_at"],
            "event_count": run_row["event_count"],
            "incident_count": run_row["incident_count"],
            "merkle_root": run_row["merkle_root"],
            "report": report,
            "decisions": decisions,
        }


def save_decision(path, run_id, decision_id, action_id, decision, actor, created_at, reason):
    initialize(path)
    with connect(path) as connection:
        connection.execute(
            "INSERT OR REPLACE INTO decisions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, decision_id, action_id, decision, actor, created_at, reason),
        )


def get_decisions(path, run_id: str) -> list[dict[str, Any]]:
    initialize(path)
    with connect(path) as connection:
        rows = connection.execute("SELECT * FROM decisions WHERE run_id = ? ORDER BY created_at DESC", (run_id,)).fetchall()
        return [dict(row) for row in rows]
