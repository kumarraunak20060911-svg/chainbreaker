from chainbreaker.containment.service import plan_actions
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset


def test_life_safety_isolation_is_not_recommendable():
    plan = plan_actions(Asset("TC-14", "Traffic controller", "signal", Criticality.LIFE_SAFETY, ("signal-phase",)))
    assert plan.recommended_action_id != "isolate-host"
    assert any(action.action_type.value == "isolate_host" and not action.auto_recommendable for action in plan.frontier)
