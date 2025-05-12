# This file defines an enum that represents every stat a Pokemon has.
# Different stats influence how a Pokemon performs in battle ranging
# from the order of attacks, health, defense, and outgoing damage.

# Imports

from enum import Enum

# Define 'Stat' enum by creating a class that extends 'Enum'

class Stat(Enum):
    # Define enumerators using string literal values
    HP = "hp"
    ATTACK = "attack"
    SPECIAL_ATTACK = "special_attack"
    DEFENSE = "defense"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"

    # Define a 'format' function which converts the stat name to a formatted version
    def format(self):
        # Check which enumeration it is
        if self == Stat.HP:
            return "HP"
        elif self == Stat.ATTACK:
            return "Attack"
        elif self == Stat.SPECIAL_ATTACK:
            return "Sp. Atk"
        elif self == Stat.DEFENSE:
            return "Defense"
        elif self == Stat.SPECIAL_DEFENSE:
            return "Sp. Def"
        elif self == Stat.SPEED:
            return "Speed"

        # Define a 'format_short' function which converts the stat name to a shorter formatted version
    def format_short(self):
        # Check which enumeration it is
        if self == Stat.HP:
            return "HP"
        elif self == Stat.ATTACK:
            return "Atk"
        elif self == Stat.SPECIAL_ATTACK:
            return "Sp. Atk"
        elif self == Stat.DEFENSE:
            return "Def"
        elif self == Stat.SPECIAL_DEFENSE:
            return "Sp. Def"
        elif self == Stat.SPEED:
            return "Spe"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value from kebab-case to snake_case because value may be provided
        # directly from Pokemon API which uses kebab-case while enumerations are in
        # snake_case
        value = value.lower().replace("-", "_")
        # Iterate all enumerations
        for entry in Stat:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value or entry.value.lower() == value:
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid stat: {value}")