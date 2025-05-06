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