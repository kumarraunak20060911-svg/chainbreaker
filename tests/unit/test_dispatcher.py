from chainbreaker.containment.dispatcher import generate_soar_payload, generate_firewall_remediation
from chainbreaker.domain.enums import ActionType, Criticality
from chainbreaker.domain.models import CandidateAction


def test_soar_payload_generation():
    action = CandidateAction(
        action_id="cut-session",
        action_type=ActionType.REVOKE_SESSION,
        target_id="TC-14",
        evidence_severed=0.85,
        collateral_cost=10.0,
        criticality=Criticality.ESSENTIAL,
        auto_recommendable=True,
        reason="Revoke operator session",
        affected_services=("session",),
    )
    payload = generate_soar_payload("INC-100", action, "8.8.8.8", "TC-14", "rcpt-1", "Analyst John")
    assert payload["soar_version"] == "2.0"
    assert payload["incident_id"] == "INC-100"
    assert payload["action"]["action_type"] == ActionType.REVOKE_SESSION.value
    assert payload["action"]["evidence_severance_pct"] == 85.0
    assert payload["execution_target"]["fail_safe_locked"] is False


def test_firewall_remediation_generation():
    cmd = generate_firewall_remediation(ActionType.REVOKE_SESSION, "ops_k", "198.51.100.10")
    assert "openvpn-control kill-session" in cmd
    assert "iptables -I FORWARD 1 -s 198.51.100.10 -j DROP" in cmd

    mqtt_cmd = generate_firewall_remediation(ActionType.BLOCK_COMMAND, "TC-14")
    assert "mosquitto_ctrl dynsec createAcl deny" in mqtt_cmd
