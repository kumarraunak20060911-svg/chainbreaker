from __future__ import annotations

from bisect import bisect_left
from dataclasses import dataclass
from ipaddress import ip_address
from math import exp, log
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class LinkObservation:
    left_event_id: str
    right_event_id: str
    entity_type: str
    entity_value: str
    delta_seconds: float
    label: int | None = None
    public_wifi_nat: bool = False
    rare_external_ip: bool = False


@dataclass(frozen=True, slots=True)
class ScoredLink:
    observation: LinkObservation
    entity_probability: float
    weight: float
    probability: float
    explanation: str
    time_decay: float
    nat_penalty_applied: bool
    external_boost_applied: bool
    calibration_status: str


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    samples: int
    positives: int
    brier_score: float


class IsotonicCalibrator:
    def __init__(self) -> None:
        self._scores: tuple[float, ...] = ()
        self._probabilities: tuple[float, ...] = ()

    def fit(self, scores: Sequence[float], labels: Sequence[int]) -> None:
        blocks: list[list[float]] = []
        for score, label in sorted(zip(scores, labels)):
            blocks.append([score, score, float(label), 1.0])
            while len(blocks) >= 2 and blocks[-2][2] / blocks[-2][3] > blocks[-1][2] / blocks[-1][3]:
                right, left = blocks.pop(), blocks.pop()
                blocks.append([left[0], right[1], left[2] + right[2], left[3] + right[3]])
        self._scores = tuple(block[1] for block in blocks)
        self._probabilities = tuple(block[2] / block[3] for block in blocks)

    @property
    def fitted(self) -> bool:
        return bool(self._scores)

    def predict(self, score: float) -> float:
        if not self._scores:
            return 1.0 / (1.0 + exp(-((score - 2.0) / 1.5)))
        return self._probabilities[min(bisect_left(self._scores, score), len(self._probabilities) - 1)]


class EvidenceLinkEngine:
    def __init__(self, entity_counts: Mapping[str, Mapping[str, int | float]], *, nat_penalty: float = 0.03, time_constants: Mapping[str, float] | None = None) -> None:
        self.counts = {kind: {value: float(count) for value, count in values.items()} for kind, values in entity_counts.items()}
        self.constants = {"ip": 900.0, "account": 1800.0, "host": 3600.0, "device": 7200.0, "peer": 7200.0, "domain": 900.0, "session": 600.0, "topic": 1800.0, **(time_constants or {})}
        self.nat_penalty = nat_penalty
        self.calibrator = IsotonicCalibrator()
        self.report = CalibrationReport(0, 0, float("nan"))

    def probability(self, entity_type: str, entity_value: str) -> float:
        values = self.counts.get(entity_type.lower(), {})
        total = sum(values.values())
        vocabulary = max(1, len(values))
        return (values.get(entity_value, 0.0) + 0.5) / (total + 0.5 * (vocabulary + 1))

    @staticmethod
    def _external(value: str) -> bool:
        try:
            address = ip_address(value)
            return not (address.is_private or address.is_loopback or address.is_reserved or address.is_link_local)
        except ValueError:
            return False

    def score(self, observation: LinkObservation) -> ScoredLink:
        if observation.delta_seconds < 0:
            raise ValueError("delta_seconds cannot be negative")
        p_entity = max(self.probability(observation.entity_type, observation.entity_value), 1e-12)
        decay = exp(-observation.delta_seconds / self.constants.get(observation.entity_type.lower(), 900.0))
        weight = -log(p_entity) * decay
        is_nat = observation.public_wifi_nat or observation.entity_type.lower() in {"public_wifi_nat", "wifi_nat", "cgnat"}
        if is_nat:
            weight *= self.nat_penalty
            explanation = "shared public Wi-Fi NAT down-weighted"
        elif (observation.rare_external_ip or self._external(observation.entity_value)) and p_entity <= 0.5:
            weight *= 1.15
            explanation = "rare external IP strengthened"
        else:
            explanation = "rarity and time decay applied"
        return ScoredLink(
            observation,
            p_entity,
            weight,
            self.calibrator.predict(weight),
            explanation,
            decay,
            is_nat,
            (not is_nat and (observation.rare_external_ip or self._external(observation.entity_value)) and p_entity <= 0.5),
            "isotonic" if self.calibrator.fitted else "fallback",
        )

    def fit_isotonic(self, observations: Iterable[LinkObservation]) -> CalibrationReport:
        labelled = [item for item in observations if item.label is not None]
        scores = [self.score(item).weight for item in labelled]
        labels: list[int] = []
        for item in labelled:
            if item.label is None:
                continue
            labels.append(int(item.label))
        if not labelled:
            self.report = CalibrationReport(0, 0, float("nan"))
            return self.report
        self.calibrator.fit(scores, labels)
        brier = sum((self.calibrator.predict(score) - label) ** 2 for score, label in zip(scores, labels)) / len(labels)
        self.report = CalibrationReport(len(labels), sum(labels), brier)
        return self.report


def link_events(left_event_id: str, right_event_id: str, entity_type: str, entity_value: str, delta_seconds: float, engine: EvidenceLinkEngine, *, public_wifi_nat: bool = False) -> ScoredLink:
    return engine.score(LinkObservation(left_event_id, right_event_id, entity_type, entity_value, delta_seconds, public_wifi_nat=public_wifi_nat))
