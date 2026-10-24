from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents/{run_id}/report")
def report(run_id: str):
    run = RUNS.get(run_id) or latest()
    return run["report"]


@router.get("/incidents/{run_id}/report/verify/{row_index}")
def verify_row(run_id: str, row_index: int):
    run = RUNS.get(run_id) or latest()
    if row_index < 0 or row_index >= len(run["events"]):
        raise HTTPException(404, "row index not found")
    proof = run["tree"].proof(row_index)
    return {"row_index": row_index, "row_id": run["events"][row_index].row_id, "verified": run["tree"].verify(proof), "root": run["tree"].root}
