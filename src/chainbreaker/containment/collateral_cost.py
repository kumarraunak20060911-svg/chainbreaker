from chainbreaker.domain.enums import Criticality
from chainbreaker.domain.models import Asset


def collateral_cost(asset: Asset) -> float:
    multiplier = {Criticality.LIFE_SAFETY: 1000.0, Criticality.ESSENTIAL: 100.0, Criticality.CONVENIENCE: 1.0}[asset.criticality]
    return multiplier * max(1, len(asset.baseline_services))
