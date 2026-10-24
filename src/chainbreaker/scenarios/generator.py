from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def central_district_rows() -> list[dict[str, object]]:
    """Scenario 1: Municipal Traffic Controller Intrusion (Central District).
    Attacker conducts password spray, logs into operator account via VPN, pivots to IoT gateway,
    issues off-window set-phase control command to traffic controller TC-14, and initiates DNS beaconing.
    """
    start = datetime(2026, 10, 24, 2, 10, tzinfo=timezone.utc)
    return [
        {"event_id": "evt-001", "row_id": "row-001", "timestamp": start.isoformat(), "source": "auth", "event_type": "login_failure", "account": "ops_k", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "evt-002", "row_id": "row-002", "timestamp": (start + timedelta(seconds=10)).isoformat(), "source": "auth", "event_type": "login_failure", "account": "ops_m", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "evt-003", "row_id": "row-003", "timestamp": (start + timedelta(seconds=20)).isoformat(), "source": "auth", "event_type": "login_failure", "account": "vendor_a", "ip": "10.20.0.8", "success": "false"},
        {"event_id": "evt-004", "row_id": "row-004", "timestamp": (start + timedelta(minutes=4)).isoformat(), "source": "vpn", "event_type": "login_success", "account": "ops_k", "ip": "8.8.8.8", "success": "true", "session_id": "sess-ops-k"},
        {"event_id": "evt-005", "row_id": "row-005", "timestamp": (start + timedelta(minutes=6)).isoformat(), "source": "iot", "event_type": "gateway_pivot", "account": "ops_k", "host": "GW-3", "device_id": "GW-3", "device_class": "gateway", "peer": "vpn-session", "payload_size": "128", "command": "route"},
        {"event_id": "evt-005a", "row_id": "row-005a", "timestamp": (start + timedelta(minutes=7)).isoformat(), "source": "iot", "event_type": "telemetry", "device_id": "TC-14", "device_class": "signal-controller", "peer": "GW-3", "payload_size": "96", "command": "telemetry"},
        {"event_id": "evt-005b", "row_id": "row-005b", "timestamp": (start + timedelta(minutes=8)).isoformat(), "source": "iot", "event_type": "telemetry", "device_id": "TC-14", "device_class": "signal-controller", "peer": "GW-3", "payload_size": "98", "command": "telemetry"},
        {"event_id": "evt-006", "row_id": "row-006", "timestamp": (start + timedelta(minutes=9)).isoformat(), "source": "iot", "event_type": "control_command", "device_id": "TC-14", "device_class": "signal-controller", "peer": "GW-3", "payload_size": "1024", "command": "set-phase"},
        {"event_id": "evt-007", "row_id": "row-007", "timestamp": (start + timedelta(minutes=11)).isoformat(), "source": "dns", "event_type": "dns_query", "host": "GW-3", "ip": "8.8.8.8", "domain": "q7k2m9x4v8z1-control.example", "metadata_url": ""},
    ]


def camera_to_charger_rows() -> list[dict[str, object]]:
    """Scenario 2: Hijacked CCTV Camera Pivot to EV Charger Grid (Section 8 of Proposal).
    Attacker compromises perimeter camera CAM-22, beacons to rare domain trusted-update.example,
    and reaches fast-charger manager EV-08 to inject start-charge command.
    """
    start = datetime(2026, 10, 24, 3, 10, tzinfo=timezone.utc)
    return [
        {"event_id": "cam-001", "row_id": "cam-row-001", "timestamp": start.isoformat(), "source": "iot", "event_type": "camera_telemetry", "device_id": "CAM-22", "device_class": "camera", "peer": "camera-gateway", "payload_size": "64", "command": "telemetry", "account": "cam-service"},
        {"event_id": "cam-002", "row_id": "cam-row-002", "timestamp": (start + timedelta(minutes=3)).isoformat(), "source": "dns", "event_type": "dns_query", "host": "CAM-22", "device_id": "CAM-22", "domain": "trusted-update.example", "first_seen": "true"},
        {"event_id": "cam-003", "row_id": "cam-row-003", "timestamp": (start + timedelta(minutes=5)).isoformat(), "source": "iot", "event_type": "camera_beacon", "device_id": "CAM-22", "device_class": "camera", "peer": "rare-domain", "payload_size": "512", "command": "telemetry", "domain": "trusted-update.example"},
        {"event_id": "cam-004", "row_id": "cam-row-004", "timestamp": (start + timedelta(minutes=6)).isoformat(), "source": "iot", "event_type": "charger_manager_access", "device_id": "EV-08", "device_class": "ev-charger", "peer": "CAM-22", "payload_size": "900", "command": "start-charge"},
        {"event_id": "cam-005", "row_id": "cam-row-005", "timestamp": (start + timedelta(minutes=8)).isoformat(), "source": "iot", "event_type": "control_command", "device_id": "EV-08", "device_class": "ev-charger", "peer": "CAM-22", "payload_size": "2048", "command": "max-draw-override"},
    ]


def university_security_rows() -> list[dict[str, object]]:
    """Scenario 3: University Infrastructure Intrusion (Section 8 of Proposal).
    Student credential access via campus-NAT, VPN access, grade portal traversal,
    DNS beaconing, cleanroom camera unauthorized export, and faculty password spraying.
    """
    start = datetime(2026, 10, 24, 9, 0, tzinfo=timezone.utc)
    rows: list[dict[str, object]] = [
        {"event_id": "uni-001", "row_id": "uni-row-001", "timestamp": start.isoformat(), "source": "auth", "event_type": "login_success", "account": "student-42", "ip": "10.10.0.5", "success": "true", "network_zone": "campus-nat"},
        {"event_id": "uni-002", "row_id": "uni-row-002", "timestamp": (start + timedelta(minutes=2)).isoformat(), "source": "vpn", "event_type": "vpn_connect", "account": "student-42", "ip": "203.0.113.20", "session_id": "uni-session-42", "success": "true"},
        {"event_id": "uni-003", "row_id": "uni-row-003", "timestamp": (start + timedelta(minutes=3)).isoformat(), "source": "portal", "event_type": "web_request", "account": "student-42", "host": "portal-app-1", "ip": "203.0.113.20", "domain": "portal.university.example", "metadata_url": "/grades"},
        {"event_id": "uni-004", "row_id": "uni-row-004", "timestamp": (start + timedelta(minutes=4)).isoformat(), "source": "dns", "event_type": "dns_query", "host": "lab-workstation-7", "ip": "203.0.113.20", "domain": "x7q9m2z8-beacon.example.net", "first_seen": "true"},
        {"event_id": "uni-005", "row_id": "uni-row-005", "timestamp": (start + timedelta(minutes=5)).isoformat(), "source": "iot", "event_type": "camera_telemetry", "device_id": "LAB-CAM-7", "device_class": "camera", "peer": "lab-gateway", "command": "telemetry", "payload_size": "64"},
        {"event_id": "uni-006", "row_id": "uni-row-006", "timestamp": (start + timedelta(minutes=6)).isoformat(), "source": "iot", "event_type": "camera_control", "device_id": "LAB-CAM-7", "device_class": "camera", "peer": "unknown-external-peer", "command": "export-recording", "payload_size": "2048"},
    ]
    rows.extend({"event_id": f"uni-spray-{index}", "row_id": f"uni-spray-row-{index}", "timestamp": (start + timedelta(minutes=10, seconds=index * 8)).isoformat(), "source": "auth", "event_type": "login_failure", "account": f"faculty-{index}", "ip": "198.51.100.44", "success": "false", "network_zone": "internet"} for index in range(1, 6))
    return rows


def central_district_with_nat_surge_rows() -> list[dict[str, object]]:
    """Judges Demo Dataset: Central District attack interleaved with a benign public Wi-Fi NAT surge.
    Under Naive Linking, the 8 benign visitors on 10.0.0.40 falsely merge into the attack chain.
    Under Probabilistic Linking, the Fellegi-Sunter NAT penalty down-weights 10.0.0.40 and purges false merges.
    """
    rows = list(central_district_rows())
    start = datetime(2026, 10, 24, 2, 12, tzinfo=timezone.utc)
    # Add 8 benign visitors sharing public Wi-Fi NAT IP 10.0.0.40
    for i in range(8):
        rows.append({
            "event_id": f"wifi-nat-{i}",
            "row_id": f"wifi-row-{i}",
            "timestamp": (start + timedelta(seconds=i * 20)).isoformat(),
            "source": "auth",
            "event_type": "login_success",
            "account": f"citizen-{i}",
            "ip": "10.0.0.40",
            "network_zone": "public-wifi",
            "public_wifi_nat": "true",
            "success": "true",
        })
    return sorted(rows, key=lambda r: str(r["timestamp"]))


def write_central_district(directory: str | Path) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    rows = central_district_rows()
    with (directory / "events.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=sorted({key for row in rows for key in row}))
        writer.writeheader(); writer.writerows(rows)
    with (directory / "assets.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["asset_id", "name", "asset_type", "criticality", "baseline_services"])
        writer.writeheader(); writer.writerows(__import__("chainbreaker.scenarios.city_profiles", fromlist=["CENTRAL_DISTRICT_ASSETS"]).CENTRAL_DISTRICT_ASSETS)
    (directory / "device_inventory.csv").write_text("device_id,device_class,criticality,allowed_peers,allowed_commands\nGW-3,gateway,essential,vpn-session,route\nTC-14,signal-controller,life-safety,GW-3,telemetry\n")
    (directory / "ground_truth.json").write_text(json.dumps({
        "scenario": "spray-to-traffic-controller",
        "attack_event_ids": ["evt-004", "evt-005", "evt-006", "evt-007"],
        "expected_stages": ["initial-access", "lateral-movement", "impact", "command-and-control"],
        "benign_event_ids": ["evt-001", "evt-002", "evt-003", "evt-005a", "evt-005b"],
    }, indent=2))
