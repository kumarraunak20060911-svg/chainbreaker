from .enums import ActionType, Criticality


def action_allowed(action_type: ActionType, criticality: Criticality) -> bool:
    return not (action_type is ActionType.ISOLATE_HOST and criticality is Criticality.LIFE_SAFETY)


def approval_required(action_type: ActionType, criticality: Criticality) -> bool:
    return True
