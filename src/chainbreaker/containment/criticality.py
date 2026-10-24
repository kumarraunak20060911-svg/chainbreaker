from chainbreaker.domain.enums import Criticality


def severity_multiplier(criticality: Criticality) -> float:
    return {Criticality.LIFE_SAFETY: 1000.0, Criticality.ESSENTIAL: 100.0, Criticality.CONVENIENCE: 1.0}[criticality]
