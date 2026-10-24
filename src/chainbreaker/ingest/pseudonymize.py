from __future__ import annotations

import hashlib
import hmac
from dataclasses import replace
from typing import Iterable

from chainbreaker.domain.models import Event


def pseudonym(value: str | None, key: bytes) -> str | None:
    if not value:
        return value
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()[:16]


def pseudonymize_events(events: Iterable[Event], key: bytes) -> list[Event]:
    fields = ("account", "host", "ip", "device_id", "peer", "domain", "session_id")
    output = []
    for event in events:
        values = {field: pseudonym(getattr(event, field), key) for field in fields}
        metadata = dict(event.metadata)
        if event.ip and event.ip.startswith(("10.", "172.16.", "192.168.")):
            metadata["public_wifi_nat"] = True
        elif event.ip:
            metadata["external_ip"] = True
        output.append(replace(event, metadata=metadata, **values))
    return output
