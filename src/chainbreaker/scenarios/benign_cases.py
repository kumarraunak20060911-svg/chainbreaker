from __future__ import annotations

from datetime import datetime, timedelta, timezone


def benign_case_names() -> tuple[str, ...]:
    return ("scheduled firmware push", "rush-hour telemetry spike", "public Wi-Fi NAT surge", "contractor bulk login")


def benign_near_miss_rows() -> dict[str, list[dict[str, object]]]:
    start = datetime(2026, 10, 24, 8, 0, tzinfo=timezone.utc)
    return {
        "scheduled firmware push": [
            {"event_id": f"fw-{index}", "timestamp": (start + timedelta(minutes=index)).isoformat(), "source": "iot", "event_type": "firmware_push", "device_id": "TC-14", "device_class": "signal-controller", "peer": "vendor-maintenance", "command": "firmware-update", "network_zone": "maintenance"}
            for index in range(3)
        ],
        "rush-hour telemetry spike": [
            {"event_id": f"rush-{index}", "timestamp": (start + timedelta(seconds=index * 10)).isoformat(), "source": "iot", "event_type": "telemetry", "device_id": "METER-9", "device_class": "meter", "peer": "meter-gateway", "command": "telemetry", "payload_size": 128}
            for index in range(12)
        ],
        "public Wi-Fi NAT surge": [
            {"event_id": f"wifi-{index}", "timestamp": (start + timedelta(seconds=index * 15)).isoformat(), "source": "auth", "event_type": "login_success", "account": f"visitor-{index}", "ip": "10.0.0.40", "network_zone": "public-wifi", "public_wifi_nat": "true", "success": "true"}
            for index in range(8)
        ],
        "contractor bulk login": [
            {"event_id": f"contractor-{index}", "timestamp": (start + timedelta(minutes=index)).isoformat(), "source": "auth", "event_type": "login_success", "account": f"contractor-{index}", "ip": "198.51.100.20", "network_zone": "vendor-vpn", "success": "true"}
            for index in range(6)
        ],
    }
