from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InMemoryRunStore:
    runs: dict[str, object]

    def __init__(self):
        self.runs = {}

    def put(self, run_id, value):
        self.runs[run_id] = value

    def get(self, run_id):
        return self.runs.get(run_id)
