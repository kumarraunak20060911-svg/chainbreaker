from chainbreaker.detection.iot import build_profile, detect_iot
from chainbreaker.ingest.service import ingest_rows
from chainbreaker.scenarios.generator import central_district_rows


def test_iot_detector_finds_off_window_command():
    events = ingest_rows(central_district_rows())
    baseline = [event for event in events if event.device_class == "signal-controller" and event.command != "set-phase"]
    profiles = {"signal-controller": build_profile("signal-controller", baseline)} if baseline else {}
    assert detect_iot(events, profiles)
