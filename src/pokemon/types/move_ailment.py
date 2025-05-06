# This file defines an enum called MoveAilment which represents different
# types of ailments a move can inflict.

# Imports

from enum import Enum

# Define 'MoveAilment' enum by creating a class that extends 'Enum'

class MoveAilment(Enum):
    # Define enumerators using string literal values
    UNKNOWN = "unknown"
    NONE = "none"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FREEZE = "freeze"
    BURN = "burn"
    POISON = "poison"
    CONFUSION = "confusion"
    INFATUATION = "infatuation"
    TRAP = "trap"
    NIGHTMARE = "nightmare"
    TORMENT = "torment"
    DISABLE = "disable"
    YAWN = "yawn"
    HEAL_BLOCK = "heal_block"
    NO_TYPE_IMMUNITY = "no_type_immunity"
    LEECH_SEED = "leech_seed"
    EMBARGO = "embargo"
    PERISH_SONG = "perish_song"
    INGRAIN = "ingrain"
    SILENCE = "silence"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value from kebab-case to snake_case because value may be provided
        # directly from Pokemon API which uses kebab-case while enumerations are in
        # snake_case
        value = value.lower().replace("-", "_")
        # Iterate all enumerations
        for entry in MoveAilment:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value or entry.value.lower() == value:
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid ailment: {value}")