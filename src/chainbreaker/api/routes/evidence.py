from fastapi import APIRouter
from dataclasses import asdict

from fastapi import HTTPException

from chainbreaker.web.app import RUNS, latest

router = APIRouter()


@router.get("/incidents/{run_id}/evidence")
def evidence(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(404, "incident not found")
    return {"links": [asdict(link) for link in run["links"]], "events": [asdict(event) for event in run["events"]], "corrections": run["corrections"]}
