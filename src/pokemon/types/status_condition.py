# This file defines an enum for all status conditions a Pokemon can have.
# Status conditions affect Pokemon in varying ways in battle and persist
# until the Pokemon is healed. (ex: Paralysis, Burnt, Poisoned)

# Imports

from enum import Enum

# Define a class called 'StatusCondition' that extends 'Enum'

class StatusCondition(Enum):
    # Define enumerations using string literal values
    PARALYZED = "paralyzed" # Affected Pokemon's turn may be skipped
    BURNED = "burned" # Affected Pokemon takes some damage every turn
    POISONED = "poisoned" # Affected Pokemon takes some damage every turn
    BADLY_POISONED = "bad_poisoned" # Affected Pokemon takes increasingly more damage every turn
    SLEEPING = "sleeping" # Pokemon is temporarily prevented from using moves
    FROZEN = "frozen" # Pokemon is temporarily prevented from using moves