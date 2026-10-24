from fastapi import APIRouter

from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents/{run_id}/report")
def report(run_id: str):
    run = RUNS.get(run_id) or latest()
    return {"run_id": run["run_id"], "merkle_root": run["tree"].root, "verified_rows": len(run["events"]), "disclaimer": "No real-world action executed"}
