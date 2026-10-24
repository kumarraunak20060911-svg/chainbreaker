from __future__ import annotations

from itertools import combinations

from chainbreaker.domain.ids import stable_id
from chainbreaker.domain.models import Event, EvidenceLink

from .entity_rarity import entity_counts
from .link_weights import CalibrationReport, EvidenceLinkEngine, LinkObservation


def _shared_entities(left: Event, right: Event) -> list[tuple[str, str]]:
    fields = {
        "account": "account",
        "ip": "ip",
        "host": "host",
        "device": "device_id",
        "session": "session_id",
        "domain": "domain",
        "peer": "peer",
    }
    matches = [
        (kind, getattr(left, attribute))
        for kind, attribute in fields.items()
        if getattr(left, attribute) and getattr(left, attribute) == getattr(right, attribute)
    ]
    cross_fields = (("device_id", "peer"), ("host", "peer"), ("session_id", "peer"))
    for left_attribute, right_attribute in cross_fields:
        if getattr(left, left_attribute) and getattr(left, left_attribute) == getattr(right, right_attribute):
            matches.append(("peer", getattr(left, left_attribute)))
        if getattr(right, left_attribute) and getattr(right, left_attribute) == getattr(left, right_attribute):
            matches.append(("peer", getattr(right, left_attribute)))
    unique: list[tuple[str, str]] = []
    for match in matches:
        if match not in unique:
            unique.append(match)
    return unique


def shared_link_observations(events: list[Event]) -> list[LinkObservation]:
    ordered = sorted(events, key=lambda item: item.timestamp)
    observations: list[LinkObservation] = []
    for left, right in combinations(ordered, 2):
        delta = (right.timestamp - left.timestamp).total_seconds()
        if delta <= 0 or delta > 3600:
            continue
        for kind, value in _shared_entities(left, right):
            nat = bool(left.metadata.get("public_wifi_nat"))
            observations.append(
                LinkObservation(
                    left.event_id,
                    right.event_id,
                    kind,
                    value,
                    delta,
                    label=0 if nat else int(kind in {"account", "session", "device", "peer"} and delta <= 900),
                    public_wifi_nat=nat,
                    rare_external_ip=bool(left.metadata.get("external_ip")),
                )
            )
            break
    return observations


def calibration_report_for(events: list[Event]) -> CalibrationReport:
    engine = EvidenceLinkEngine(entity_counts(events))
    return engine.fit_isotonic(shared_link_observations(events))


def build_links(events: list[Event], *, minimum_probability: float = 0.22, naive: bool = False) -> list[EvidenceLink]:
    """Build evidence links using either Fellegi-Sunter probabilistic weighting or naive SIEM field matching."""
    engine = EvidenceLinkEngine(entity_counts(events))
    ordered = sorted(events, key=lambda item: item.timestamp)
    engine.fit_isotonic(shared_link_observations(events))
    output: list[EvidenceLink] = []
    for left, right in combinations(ordered, 2):
        delta = (right.timestamp - left.timestamp).total_seconds()
        if delta <= 0 or delta > 3600:
            continue
        for kind, value in _shared_entities(left, right):
            is_nat = bool(left.metadata.get("public_wifi_nat") or right.metadata.get("public_wifi_nat") or (left.ip and "10.0.0.40" in left.ip))
            if naive:
                # Traditional SIEM naive field matching: ignores rarity and NAT penalty
                output.append(
                    EvidenceLink(
                        stable_id("link-naive", left.event_id, right.event_id, kind),
                        left.event_id,
                        right.event_id,
                        kind,
                        value,
                        weight=2.5,
                        probability=0.88,
                        explanation="naive shared-field match (no rarity or NAT penalty)",
                        row_ids=tuple(filter(None, (left.row_id, right.row_id))),
                        entity_probability=1.0,
                        delta_seconds=delta,
                        time_decay=1.0,
                        nat_penalty_applied=False,
                        external_ip_boost_applied=False,
                        calibration_status="naive-uncalibrated",
                    )
                )
            else:
                scored = engine.score(
                    LinkObservation(
                        left.event_id,
                        right.event_id,
                        kind,
                        value,
                        delta,
                        public_wifi_nat=is_nat,
                        rare_external_ip=bool(left.metadata.get("external_ip")),
                    )
                )
                if scored.probability >= minimum_probability:
                    output.append(
                        EvidenceLink(
                            stable_id("link", left.event_id, right.event_id, kind),
                            left.event_id,
                            right.event_id,
                            kind,
                            value,
                            scored.weight,
                            scored.probability,
                            scored.explanation,
                            tuple(filter(None, (left.row_id, right.row_id))),
                            scored.entity_probability,
                            delta,
                            scored.time_decay,
                            scored.nat_penalty_applied,
                            scored.external_boost_applied,
                            scored.calibration_status,
                        )
                    )
            break
    return output
