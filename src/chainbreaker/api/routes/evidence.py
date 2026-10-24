from fastapi import APIRouter
from dataclasses import asdict

from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents/{run_id}/evidence")
def evidence(run_id: str):
    run = RUNS.get(run_id) or latest()
    return {"links": [asdict(link) for link in run["links"]], "events": [asdict(event) for event in run["events"]]}
