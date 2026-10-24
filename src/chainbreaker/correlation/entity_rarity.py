from collections import Counter
from typing import Iterable

from chainbreaker.domain.models import Event


def entity_counts(events: Iterable[Event]) -> dict[str, dict[str, int]]:
    output: dict[str, Counter[str]] = {}
    for event in events:
        for kind, value in (("account", event.account), ("ip", event.ip), ("host", event.host), ("device", event.device_id), ("peer", event.peer), ("domain", event.domain), ("session", event.session_id), ("topic", event.topic)):
            if value:
                output.setdefault(kind, Counter())[value] += 1
    return {kind: dict(counter) for kind, counter in output.items()}
