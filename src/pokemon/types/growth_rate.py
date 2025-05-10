# This file contains the GrowthRate enum which represents
# the rate at which a Pokemon gains experience and levels
# up. (ex: Fast, Slow, Erratic, etc)

# Imports

from enum import Enum

# Define 'GrowthRate' enum by creating a class that extends 'Enum'
class GrowthRate(Enum):
    # Define enumerations using string literal values
    FAST = "fast",
    MEDIUM_FAST = "medium",
    MEDIUM_SLOW = "medium_slow",
    SLOW = "slow",
    ERRATIC = "slow_then_very_fast",
    FLUCTUATING = "fast_then_very_slow"

    # Define a function to calculate the experience points needed to level up
    # Formulas are derived from Bulbapedia: https://bulbapedia.bulbagarden.net/wiki/Experience#Fast
    def get_experience_needed(self, next_level: int):
        if self == GrowthRate.FAST:
            return (4 * next_level**3) / 5
        elif self == GrowthRate.MEDIUM_FAST:
            return next_level**3
        elif self == GrowthRate.MEDIUM_SLOW:
            return (6/5) * next_level**3 - 15 * next_level**2 + 100 * next_level - 140
        elif self == GrowthRate.SLOW:
            return (5 * next_level**3) / 4
        elif self == GrowthRate.ERRATIC:
            if next_level < 50:
                return (next_level**3 * (100 - next_level)) / 50
            elif next_level < 68:
                return (next_level**3 * (100 - next_level)) / 100
            elif next_level < 98:
                return (next_level * ((1911 - next_level * 10) / 3)) / 500
            else:
                return (next_level**3 * (160 - next_level)) / 100
        elif self == GrowthRate.FLUCTUATING:
            if next_level < 15:
                return (next_level * ((next_level + 1) / 3) + 25) / 50
            elif next_level < 36:
                return (next_level**3 * (next_level + 14)) / 50
            else:
                return (next_level**3 * (next_level / 2) + 32) / 50

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value from kebab-case to snake_case because value may be provided
        # directly from Pokemon API which uses kebab-case while enumerations are in
        # snake_case
        value = value.replace("-", "_")
        # Iterate all enumerations
        for rate in GrowthRate:
            if rate.name.lower() == value.lower() or rate.value[0] == value.lower():
                return rate
        raise KeyError(f"Unknown growth rate: {value}")