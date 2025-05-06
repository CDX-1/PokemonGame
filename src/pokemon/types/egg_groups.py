# This file contains an enum that represents possible egg groups a
# species can fall into. (ex: Monster, Flying, Dragon, etc). Egg groups
# are used to determine if two Pokemon are capable of producing an egg
# by searching for at least one matching egg group between the Pokemon.

# Imports

from enum import Enum

# Define 'EggGroup' enum by creating a class that extends 'Enum'

class EggGroup(Enum):
    # Define enumerations using string literal values
    MONSTER = "monster",
    WATER_1 = "water1"
    WATER_2 = "water2"
    WATER_3 = "water3"
    BUG = "bug"
    FLYING = "flying"
    GROUND = "ground"
    FAIRY = "fairy"
    PLANT = "plant"
    HUMANSHAPE = "humanshape"
    MINERAL = "mineral"
    INDETERMINATE = "indeterminate"
    DITTO = "ditto"
    DRAGON = "dragon"
    NO_EGGS = "no_eggs"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value from kebab-case to snake_case because value may be provided
        # directly from Pokemon API which uses kebab-case while enumerations are in
        # snake_case
        value = value.replace("-", "_")
        # Iterate all enumerations
        for group in EggGroup:
            # Check if current enumeration's name or value matches the 'value' argument
            if group.name.lower() == value.lower() or group.value == value.lower():
                # Return matching enumeration
                return group
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Unknown egg group: {value}")