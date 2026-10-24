from fastapi import APIRouter, HTTPException
from dataclasses import asdict

from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents")
def incidents():
    run = latest()
    return {"run_id": run["run_id"], "summary": run["summary"], "metrics": run["metrics"], "findings": [asdict(finding) for finding in run["findings"]]}


@router.get("/incidents/{run_id}")
def incident(run_id: str):
    run = RUNS.get(run_id)
    if not run: raise HTTPException(404, "incident not found")
    return {"run_id": run_id, "summary": run["summary"], "metrics": run["metrics"], "incidents": run["incidents"], "chains": [asdict(chain) for chain in run["chains"]]}
