from typing import List
from app.models import Product


class RuleBase:
    """
    Base class for all filtering rules.
    """
    def apply(self, products: List[Product], component_type: str) -> List[Product]:
        raise NotImplementedError


class MinRamSizeRule(RuleBase):
    def __init__(self, min_total_gb: int):
        self.min_total_gb = min_total_gb

    def apply(self, products: List[Product], component_type: str) -> List[Product]:
        if component_type != "ram":
            return products
        return [
            p for p in products
            if p.ram_attributes.total_memory >= self.min_total_gb
        ]


def get_rules_for_purpose(purpose: str) -> list[RuleBase]:
    """
    Return a list of rules depending on the PC purpose.
    """
    if purpose == "gaming":
        return [MinRamSizeRule(16)]
    elif purpose == "office":
        return [MinRamSizeRule(8)]
    elif purpose == "development":
        return [MinRamSizeRule(32)]
    return []
