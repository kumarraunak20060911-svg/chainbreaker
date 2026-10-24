from fastapi import APIRouter
from dataclasses import asdict

from chainbreaker.containment.service import plan_actions
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset

router = APIRouter()


@router.get("/incidents/{run_id}/containment")
def containment(run_id: str):
    target = Asset("TC-14", "Traffic controller TC-14", "signal-controller", Criticality.LIFE_SAFETY, ("signal-phase",))
    plan = plan_actions(target)
    return {"recommended_action_id": plan.recommended_action_id, "frontier": [asdict(item) for item in plan.frontier]}
