from __future__ import annotations

from chainbreaker.scenarios.generator import camera_to_charger_rows, central_district_rows


SCENARIOS = {
    "spray-to-traffic-controller": (central_district_rows, {"evt-004", "evt-005", "evt-006", "evt-007"}, ("initial-access", "lateral-movement", "impact")),
    "camera-to-ev-charger": (camera_to_charger_rows, {"cam-002", "cam-003"}, ("command-and-control", "discovery")),
}


def scenario_rows(name: str) -> tuple[list[dict[str, object]], set[str], tuple[str, ...]]:
    factory, attack_ids, stages = SCENARIOS[name]
    return factory(), set(attack_ids), stages
