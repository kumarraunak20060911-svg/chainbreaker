from __future__ import annotations

from chainbreaker.domain.enums import ActionType
from chainbreaker.domain.models import Asset, CandidateAction

from .min_cut import evaluate_action
from .pareto import ParetoPlan, build_pareto_frontier


def plan_actions(target: Asset, *, primary_severance: float = .82) -> ParetoPlan:
    actions = [
        evaluate_action("revoke-session", ActionType.REVOKE_SESSION, target, primary_severance),
        evaluate_action("block-command", ActionType.BLOCK_COMMAND, target, max(.55, primary_severance - .1)),
        evaluate_action("isolate-host", ActionType.ISOLATE_HOST, target, min(1.0, primary_severance + .08)),
    ]
    return build_pareto_frontier(actions)
