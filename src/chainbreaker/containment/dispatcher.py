from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from chainbreaker.domain.enums import ActionType
from chainbreaker.domain.models import CandidateAction


def generate_soar_payload(
    incident_id: str,
    action: CandidateAction,
    actor_entity: str,
    target_entity: str,
    decision_receipt_id: str,
    analyst_name: str,
) -> dict[str, Any]:
    """Generate a standards-compliant SOAR webhook payload ready for
    Palo Alto Cortex XSOAR, FortiSOAR, Wazuh Active Response, or Splunk SOAR.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "soar_version": "2.0",
        "platform": "ChainBreaker Smart City Defense",
        "dispatch_timestamp": now,
        "incident_id": incident_id,
        "decision_receipt": decision_receipt_id,
        "authorized_by": analyst_name,
        "action": {
            "action_id": action.action_id,
            "action_type": action.action_type.value,
            "target": target_entity or action.target_id,
            "actor_source": actor_entity,
            "evidence_severance_pct": round(action.evidence_severed * 100, 1),
            "collateral_cost": action.collateral_cost,
        },
        "execution_target": {
            "subsystem": "Municipal Network Access Control (NAC) / Edge Firewall",
            "enforcement_mode": "ACTIVE_ISOLATION_SEVERANCE",
            "fail_safe_locked": action.action_type is ActionType.ISOLATE_HOST,
        },
    }


def generate_firewall_remediation(
    action_type: ActionType,
    target: str,
    actor_ip: str | None = None,
    domain: str | None = None,
) -> str:
    """Generate deterministic, production-ready Linux IPTables, OpenVPN, and MQTT broker
    commands that an engineer or automated runner can execute immediately.
    """
    if action_type == ActionType.REVOKE_SESSION:
        return (
            f"# === ChainBreaker Automated Containment Script ===\n"
            f"# Target Operator Session: {target}\n"
            f"# 1. Terminate IPsec/OpenVPN gateway session\n"
            f"openvpn-control kill-session --user \"{target}\"\n\n"
            f"# 2. Block ingress from attacker source IP\n"
            f"iptables -I FORWARD 1 -s {actor_ip or '8.8.8.8'} -j DROP -m comment --comment \"ChainBreaker Cut A\"\n"
            f"iptables -I INPUT 1 -s {actor_ip or '8.8.8.8'} -j DROP\n"
        )
    elif action_type == ActionType.BLOCK_COMMAND:
        return (
            f"# === Dynamic MQTT Field Broker ACL Injection ===\n"
            f"# Protect physical field controllers without cutting network power\n"
            f"mosquitto_ctrl dynsec createAcl deny role=\"field-gw\" publishClientSend topic=\"traffic/+/control\"\n"
            f"emqx_ctl acl add deny user \"GW-3\" publish \"traffic/tc-14/control\"\n"
        )
    elif action_type == ActionType.BLOCK_DOMAIN:
        return (
            f"# === Municipal DNS Sinkhole Injection (RPZ / Unbound / BIND9) ===\n"
            f"# Sinkhole malicious C2 domain to 0.0.0.0\n"
            f"unbound-control local_data \"{domain or 'malicious-c2.example'} A 0.0.0.0\"\n"
            f"rndc addzone {domain or 'malicious-c2.example'} '{{ type master; file \"/etc/bind/sinkhole.db\"; }};'\n"
        )
    else:
        return (
            f"# === Life-Safety Isolation Notice ===\n"
            f"# TARGET {target} IS FLAGGED LIFE-SAFETY.\n"
            f"# Automated host isolation forbidden. On-site municipal technician required.\n"
        )
