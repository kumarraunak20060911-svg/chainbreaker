from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone


def build_case_report(run_id, incident, chain, findings, links, merkle_root):
    return {
        "report_id": f"report-{run_id}",
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident": incident,
        "attack_chain": chain,
        "findings": findings,
        "evidence_links": links,
        "merkle_root": merkle_root,
        "disclaimer": "Simulation and investigation output only. No containment action was executed.",
    }
