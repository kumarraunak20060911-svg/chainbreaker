from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, cast
from datetime import datetime, timezone


def _plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _plain(item) for key, item in asdict(cast(Any, value)).items()}
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def build_case_report(run_id, incident, chain, findings, links, merkle_root, *, calibration=None, containment=None, row_proofs=None):
    return {
        "report_id": f"report-{run_id}",
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident": _plain(incident),
        "attack_chain": _plain(chain),
        "findings": _plain(findings),
        "evidence_links": _plain(links),
        "merkle_root": merkle_root,
        "calibration": _plain(calibration),
        "containment": _plain(containment),
        "row_proofs": _plain(row_proofs),
        "disclaimer": "Simulation and investigation output only. No containment action was executed.",
    }
