from datetime import datetime, timezone
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from chainbreaker.storage.repositories import save_decision, save_run
from chainbreaker.web.app import RUNS, latest

router = APIRouter()


class DecisionRequest(BaseModel):
    action_id: str
    decision: str
    actor: str
    reason: str = ""
    on_site_operator: bool = False


@router.get("/incidents/{run_id}/containment")
def containment(run_id: str):
    run = RUNS.get(run_id) or latest()
    return {
        "recommended_action_id": run["containment"].recommended_action_id,
        "frontier": [asdict(item) for item in run["containment"].frontier],
        "replays": run["containment"].replays,
        "decisions": run.get("decisions", []),
    }


@router.post("/incidents/{run_id}/containment/decisions")
def log_decision(run_id: str, request: DecisionRequest):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(404, "incident not found")
    actions = {action.action_id: action for action in run["containment"].frontier}
    action = actions.get(request.action_id)
    if action is None:
        raise HTTPException(404, "candidate action not found")
    decision = request.decision.strip().lower()
    if decision not in {"approved", "rejected", "deferred"}:
        raise HTTPException(422, "decision must be approved, rejected, or deferred")
    if decision == "approved" and not action.auto_recommendable and not request.on_site_operator:
        raise HTTPException(409, "life-safety isolation requires explicit on-site operator confirmation")
    record = {
        "decision_id": f"decision-{uuid4().hex[:10]}",
        "action_id": action.action_id,
        "decision": decision,
        "actor": request.actor,
        "reason": request.reason,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "executed": False,
        "on_site_operator": request.on_site_operator,
    }
    run.setdefault("decisions", []).append(record)
    run["report"]["decisions"] = run["decisions"]
    save_decision(Path("runtime/databases/chainbreaker.sqlite3"), run_id, record["decision_id"], action.action_id, decision, request.actor, record["created_at"], request.reason)
    save_run(Path("runtime/databases/chainbreaker.sqlite3"), run_id, run["report"]["generated_at"], run["events"], run["findings"], run["tree"].root, incident_count=len(run["incidents"]), links=run["links"], report=run["report"])
    return record
