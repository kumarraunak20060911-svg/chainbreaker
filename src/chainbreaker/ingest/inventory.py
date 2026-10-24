from __future__ import annotations

from typing import Any, Iterable, Mapping

from chainbreaker.detection.iot import DeviceProfile, build_profile
from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset, Event


def _items(value: Any) -> tuple[str, ...]:
    if value in (None, ""):
        return ()
    if isinstance(value, (list, tuple, set)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


def asset_from_row(row: Mapping[str, Any]) -> Asset:
    return Asset(
        asset_id=str(row["asset_id"]),
        name=str(row.get("name") or row["asset_id"]),
        asset_type=str(row.get("asset_type") or "unknown"),
        criticality=Criticality(str(row.get("criticality") or Criticality.CONVENIENCE)),
        baseline_services=_items(row.get("baseline_services")),
        owner=str(row.get("owner") or ""),
    )


def assets_from_rows(rows: Iterable[Mapping[str, Any]]) -> dict[str, Asset]:
    return {asset.asset_id: asset for asset in (asset_from_row(row) for row in rows) if asset.asset_id}


def profiles_from_inventory(events: list[Event], rows: Iterable[Mapping[str, Any]]) -> dict[str, DeviceProfile]:
    inventory = {str(row.get("device_id")): row for row in rows if row.get("device_id")}
    profiles: dict[str, DeviceProfile] = {}
    for device_class in {event.device_class for event in events if event.device_class}:
        baseline = [event for event in events if event.device_class == device_class]
        if not baseline:
            continue
        profile = build_profile(device_class or "unknown", baseline)
        rows_for_class = [row for row in inventory.values() if row.get("device_class") == device_class]
        if rows_for_class:
            allowed_peers = set(profile.allowed_peers)
            allowed_commands = set(profile.allowed_commands)
            for row in rows_for_class:
                allowed_peers.update(_items(row.get("allowed_peers")))
                allowed_commands.update(_items(row.get("allowed_commands")))
            from dataclasses import replace
            profile = replace(profile, allowed_peers=frozenset(allowed_peers), allowed_commands=frozenset(allowed_commands))
        profiles[device_class] = profile
    return profiles
