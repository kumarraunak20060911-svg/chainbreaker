from chainbreaker.reporting.societal_impact import compute_societal_impact
from chainbreaker.domain.enums import Criticality


def test_societal_impact_life_safety_asset():
    impact = compute_societal_impact(
        target_asset_name="Traffic Controller TC-14",
        target_criticality=Criticality.LIFE_SAFETY,
        events_count=100,
        findings_count=12,
        brier_score=0.17,
        time_to_detect_seconds=120.0,
    )
    assert impact["resilience_score"] >= 80.0
    assert impact["public_safety_status"] == "LIFE-SAFETY INTEGRITY PRESERVED"
    assert impact["economic_loss_averted_usd"] > 100000
    assert "100% HMAC" in impact["citizen_privacy_index"]


def test_societal_impact_essential_asset():
    impact = compute_societal_impact(
        target_asset_name="Fast Charger Manager EV-08",
        target_criticality=Criticality.ESSENTIAL,
        events_count=50,
        findings_count=5,
        brier_score=0.20,
        time_to_detect_seconds=180.0,
    )
    assert impact["economic_loss_averted_usd"] > 50000
