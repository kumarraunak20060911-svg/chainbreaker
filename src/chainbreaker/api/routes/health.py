from fastapi import APIRouter
from chainbreaker.storage.engine import dependency_health
from chainbreaker.observability import METRICS

router = APIRouter()


@router.get("/health")
def health():
    dependency = dependency_health()
    return {"status": "ok" if dependency["status"] == "ok" else "degraded", "service": "chainbreaker", "dependencies": dependency, "metrics": dict(METRICS)}
