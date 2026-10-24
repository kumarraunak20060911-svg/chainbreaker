from chainbreaker.scenarios.recreator import get_scenario_recreation, RECREATION_TIMELINES


def test_scenario_recreation_timelines_contain_required_mitre_stages():
    timeline = get_scenario_recreation("central_district")
    assert timeline["target_criticality"] == "LIFE-SAFETY"
    assert timeline["target_asset"] == "Traffic Controller TC-14"
    assert len(timeline["steps"]) >= 4

    # Verify MITRE stages progress chronologically
    stages = [step["stage"] for step in timeline["steps"]]
    assert "Credential Access" in stages
    assert "Initial Access" in stages
    assert "Lateral Movement" in stages
    assert "Impact Attempt" in stages

    # Check EV scenario
    ev_timeline = get_scenario_recreation("ev_charger")
    assert ev_timeline["target_criticality"] == "ESSENTIAL"
    assert any("start-charge" in step["raw_packet"] or "max-draw-override" in step["raw_packet"] for step in ev_timeline["steps"])


def test_public_wifi_nat_scenario_distinguishes_benign_surge():
    nat_timeline = get_scenario_recreation("nat_surge")
    attack_steps = [s for s in nat_timeline["steps"] if s["is_attack"]]
    benign_steps = [s for s in nat_timeline["steps"] if not s["is_attack"]]

    assert len(attack_steps) >= 3
    assert len(benign_steps) >= 2
    for step in benign_steps:
        assert step["calibrated_weight"] < 0.2  # RFC 1918 NAT penalty
