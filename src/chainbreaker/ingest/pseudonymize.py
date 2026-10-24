from __future__ import annotations

import hashlib
import hmac
from ipaddress import ip_address
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
        zone = str(metadata.get("network_zone", "")).strip().lower()
        explicit_nat = str(metadata.get("public_wifi_nat", "")).strip().lower() in {"1", "true", "yes"}
        if explicit_nat or any(token in zone for token in ("public-wifi", "public_wifi", "nat", "cgnat")):
            metadata["public_wifi_nat"] = True
        elif event.ip:
            try:
                address = ip_address(event.ip)
                metadata["external_ip"] = not (address.is_private or address.is_loopback or address.is_reserved or address.is_link_local)
            except ValueError:
                metadata["external_ip"] = False
        metadata["pseudonymized"] = True
        output.append(replace(event, metadata=metadata, **values))
    return output
