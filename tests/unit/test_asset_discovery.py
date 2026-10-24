from chainbreaker.containment.asset_discovery import auto_discover_asset, enrich_inventory_with_discovery
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Event, EventSource
from datetime import datetime, timezone


def test_auto_discover_life_safety_traffic_controller():
    asset = auto_discover_asset("TC-99", command="set-phase", device_class="signal-controller")
    assert asset.criticality is Criticality.LIFE_SAFETY
    assert "signal-phase" in asset.baseline_services
    assert "Traffic" in asset.name


def test_auto_discover_life_safety_water_pump():
    asset = auto_discover_asset("WATER-PUMP-4", topic="scada/water/pump-4/control")
    assert asset.criticality is Criticality.LIFE_SAFETY
    assert "pressure-regulation" in asset.baseline_services


def test_auto_discover_power_substation():
    asset = auto_discover_asset("SUBSTATION-GRID-EAST", command="trip-breaker")
    assert asset.criticality is Criticality.LIFE_SAFETY
    assert "voltage-stabilization" in asset.baseline_services


def test_enrich_inventory_with_discovery():
    now = datetime.now(timezone.utc)
    events = [
        Event("e1", now, EventSource.IOT, "control", device_id="UNKNOWN-TC-12", command="set-phase"),
        Event("e2", now, EventSource.IOT, "telemetry", device_id="UNKNOWN-CAM-99", command="telemetry"),
    ]
    enriched = enrich_inventory_with_discovery({}, events)
    assert "UNKNOWN-TC-12" in enriched
    assert enriched["UNKNOWN-TC-12"].criticality is Criticality.LIFE_SAFETY
    assert "UNKNOWN-CAM-99" in enriched
    assert enriched["UNKNOWN-CAM-99"].criticality is Criticality.ESSENTIAL
