from __future__ import annotations

CENTRAL_DISTRICT_ASSETS = [
    {"asset_id": "GW-3", "name": "IoT gateway GW-3", "asset_type": "gateway", "criticality": "essential", "baseline_services": "mqtt,telemetry"},
    {"asset_id": "TC-14", "name": "Traffic controller TC-14", "asset_type": "signal-controller", "criticality": "life-safety", "baseline_services": "signal-phase,emergency-preemption"},
]

EV_NETWORK_ASSETS = [
    {"asset_id": "CAM-22", "name": "Perimeter CCTV CAM-22", "asset_type": "camera", "criticality": "convenience", "baseline_services": "rtsp,telemetry"},
    {"asset_id": "EV-08", "name": "Fast Charger Manager EV-08", "asset_type": "ev-charger", "criticality": "essential", "baseline_services": "ocpp,load-balance"},
]

UNIVERSITY_ASSETS = [
    {"asset_id": "portal-app-1", "name": "Academic Records Portal", "asset_type": "web-application", "criticality": "essential", "baseline_services": "https,grades-api"},
    {"asset_id": "lab-workstation-7", "name": "Research Lab Workstation 7", "asset_type": "workstation", "criticality": "convenience", "baseline_services": "ssh,dns"},
    {"asset_id": "LAB-CAM-7", "name": "Cleanroom Camera LAB-CAM-7", "asset_type": "camera", "criticality": "convenience", "baseline_services": "rtsp,telemetry"},
]

BENIGN_SURGE_ASSETS = [
    {"asset_id": "WIFI-GW-1", "name": "City Hall Public Wi-Fi Gateway", "asset_type": "gateway", "criticality": "convenience", "baseline_services": "dhcp,nat"},
]
