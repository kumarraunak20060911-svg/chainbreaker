from __future__ import annotations

from typing import Iterable, Mapping

from chainbreaker.domain.models import Event

from .auth import detect_auth
from .dns import detect_dns
from .finding import DetectionFinding
from .iot import DeviceProfile, detect_iot
from .portal import detect_portal


def detect_all(events: Iterable[Event], profiles: Mapping[str, DeviceProfile] | None = None) -> list[DetectionFinding]:
    items = list(events)
    return detect_auth(items) + detect_dns(items) + detect_portal(items) + detect_iot(items, profiles or {})
