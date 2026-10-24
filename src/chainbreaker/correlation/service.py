from __future__ import annotations

from itertools import combinations

from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event, EvidenceLink

from .entity_rarity import entity_counts
from .link_weights import EvidenceLinkEngine, LinkObservation


def build_links(events: list[Event], *, minimum_probability: float = 0.22) -> list[EvidenceLink]:
    engine = EvidenceLinkEngine(entity_counts(events))
    output = []
    for left, right in combinations(sorted(events, key=lambda item: item.timestamp), 2):
        delta = (right.timestamp - left.timestamp).total_seconds()
        if delta < 0 or delta > 3600:
            continue
        fields = {"account": "account", "ip": "ip", "host": "host", "device": "device_id", "session": "session_id", "domain": "domain"}
        shared = [(kind, getattr(left, attribute)) for kind, attribute in fields.items()]
        for kind, value in shared:
            if value and value == getattr(right, fields[kind]):
                scored = engine.score(LinkObservation(left.event_id, right.event_id, kind, value, delta, public_wifi_nat=bool(left.metadata.get("public_wifi_nat")), rare_external_ip=bool(left.metadata.get("external_ip"))))
                if scored.probability >= minimum_probability:
                    output.append(EvidenceLink(stable_id("link", left.event_id, right.event_id, kind), left.event_id, right.event_id, kind, value, scored.weight, scored.probability, scored.explanation, tuple(filter(None, (left.row_id, right.row_id)))))
                break
    return output
