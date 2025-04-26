from __future__ import annotations

from enum import Enum

class GrowthRate(Enum):
    ERRATIC = "erratic",
    FAST = "fast",
    MEDIUM_FAST = "medium_fast",
    MEDIUM_SLOW = "medium_slow",
    SLOW = "slow",
    FLUCTUATING = "fluctuating"

    @staticmethod
    def of(value: str) -> GrowthRate:
        for rate in GrowthRate:
            if rate.name.lower() == value.lower() or rate.value == value.lower():
                return rate
        raise KeyError(f"Unknown growth rate: {value}")