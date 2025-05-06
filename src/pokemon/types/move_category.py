# This file defines an enum that sorts moves into several different categories depending
# on the effects of the move such as damaging moves, ailment moves, or combinations of
# such categories.

# Imports

from enum import Enum

# Define 'MoveCategory' enum by creating a class that extends 'Enum'

class MoveCategory(Enum):
    # Define enumerators using string literal values
    UNKNOWN = "unknown"
    DAMAGE = "damage"
    AILMENT = "ailment"
    NET_GOOD_STATS = "net_good_stats"
    HEAL = "heal"
    DAMAGE_AILMENT = "damage+ailment"
    SWAGGER = "swagger"
    DAMAGE_LOWER = "damage+lower"
    DAMAGE_RAISE = "damage+raise"
    DAMAGE_HEAL = "damage+heal"
    OHKO = "ohko"
    WHOLE_FIELD_EFFECT = "whole_field_effect"
    FIELD_EFFECT = "field_effect"
    FORCE_SWITCH = "force_switch"
    UNIQUE = "unique"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value from kebab-case to snake_case because value may be provided
        # directly from Pokemon API which uses kebab-case while enumerations are in
        # snake_case
        value = value.lower().replace("-", "_")
        # Iterate all enumerations
        for entry in MoveCategory:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value or entry.value.lower() == value:
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid move category: {value}")