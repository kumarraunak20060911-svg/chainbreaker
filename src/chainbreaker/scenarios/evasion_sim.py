from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta, timezone

from chainbreaker.detection.service import detect_all
from chainbreaker.ingest.service import ingest_rows
from .evasion import hill_climb_evasion, evasion_knobs


def simulate_evasion_attack(rate: float = 1.0, jitter_seconds: float = 0.0, trusted_domain_c2: bool = False) -> dict[str, Any]:
    """Recreate attack sequence with evasion knobs (jitter, low-and-slow rate, trusted-domain C2).
    Evaluates detector coverage and returns the detection score and fired rules.
    """
    start = datetime(2026, 10, 24, 2, 10, tzinfo=timezone.utc)
    step = 10.0 / max(rate, 0.1)

    domain = "cdn-update.city.example" if trusted_domain_c2 else "q7k2m9x4v8z1-control.example"
    
    rows = [
        {"event_id": "ev-001", "row_id": "r-001", "timestamp": start.isoformat(), "source": "auth", "event_type": "login_failure", "account": "ops_k", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "ev-002", "row_id": "r-002", "timestamp": (start + timedelta(seconds=step + jitter_seconds * 0.3)).isoformat(), "source": "auth", "event_type": "login_failure", "account": "ops_m", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "ev-003", "row_id": "r-003", "timestamp": (start + timedelta(seconds=step * 2 + jitter_seconds * 0.6)).isoformat(), "source": "auth", "event_type": "login_failure", "account": "vendor_a", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "ev-004", "row_id": "r-004", "timestamp": (start + timedelta(minutes=4 / max(rate, 0.1))).isoformat(), "source": "vpn", "event_type": "login_success", "account": "ops_k", "ip": "8.8.8.8", "success": "true", "session_id": "sess-ops-k"},
        {"event_id": "ev-005", "row_id": "r-005", "timestamp": (start + timedelta(minutes=6 / max(rate, 0.1))).isoformat(), "source": "iot", "event_type": "gateway_pivot", "account": "ops_k", "host": "GW-3", "device_id": "GW-3", "device_class": "gateway", "peer": "vpn-session", "payload_size": "128", "command": "route"},
        {"event_id": "ev-006", "row_id": "r-006", "timestamp": (start + timedelta(minutes=9 / max(rate, 0.1))).isoformat(), "source": "iot", "event_type": "control_command", "device_id": "TC-14", "device_class": "signal-controller", "peer": "GW-3", "payload_size": "1024", "command": "set-phase"},
        {"event_id": "ev-007", "row_id": "r-007", "timestamp": (start + timedelta(minutes=11 / max(rate, 0.1) + jitter_seconds)).isoformat(), "source": "dns", "event_type": "dns_query", "host": "GW-3", "ip": "8.8.8.8", "domain": domain, "metadata_url": ""},
    ]

    events = ingest_rows(rows)
    findings = detect_all(events)

    rules_fired = [f.rule_id for f in findings]
    detection_score = len(findings)

    return {
        "rate": rate,
        "jitter_seconds": jitter_seconds,
        "trusted_domain_c2": trusted_domain_c2,
        "findings_count": len(findings),
        "rules_fired": rules_fired,
        "evaded": len(findings) <= 1,
        "c2_detected": any("DNS" in r for r in rules_fired),
        "spray_detected": any("AUTH" in r for r in rules_fired),
        "impact_detected": any("IOT" in r for r in rules_fired),
    }


def run_hill_climbing_adversary() -> dict[str, Any]:
    """Executes Section 4.E hill-climbing optimization to find evasion thresholds."""
    def score_function(knobs: dict[str, float]) -> float:
        res = simulate_evasion_attack(
            rate=knobs.get("rate", 1.0),
            jitter_seconds=knobs.get("jitter_seconds", 0.0),
            trusted_domain_c2=bool(knobs.get("trusted_domain_c2", 0.0) >= 0.5),
        )
        return float(res["findings_count"])

    optimal_knobs = hill_climb_evasion(score_function, steps=30)
    baseline_result = simulate_evasion_attack(rate=1.0, jitter_seconds=0.0, trusted_domain_c2=False)
    evaded_result = simulate_evasion_attack(
        rate=optimal_knobs.get("rate", 1.0),
        jitter_seconds=optimal_knobs.get("jitter_seconds", 0.0),
        trusted_domain_c2=bool(optimal_knobs.get("trusted_domain_c2", 0.0) >= 0.5),
    )

    return {
        "baseline": baseline_result,
        "adversary_optimal": optimal_knobs,
        "evaded_simulation": evaded_result,
        "knobs_explored": evasion_knobs(),
    }
