from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from chainbreaker.settings import Settings
from chainbreaker.storage.persistent import get_report
from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents/{run_id}/report")
def report(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        stored = get_report(run_id, "dev-organization", settings=Settings.load())
        if stored is None:
            raise HTTPException(404, "incident not found")
        return stored
    return run["report"]


@router.get("/incidents/{run_id}/report/verify/{row_index}")
def verify_row(run_id: str, row_index: int):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(404, "incident not found")
    if row_index < 0 or row_index >= len(run["events"]):
        raise HTTPException(404, "row index not found")
    proof = run["tree"].proof(row_index)
    return {"row_index": row_index, "row_id": run["events"][row_index].row_id, "verified": run["tree"].verify(proof), "root": run["tree"].root}
