# This file contains an enum that represents possible encounter types
# that a battle with a wild Pokemon can fall into. This is used to make
# certain Pokeballs more effective in certain conditions such as fishing.

# Imports

from enum import Enum

# Define 'EncounterType' enum by creating a class that extends 'Enum'

class EncounterType(Enum):
    # Define enumerations using string literal values
    GRASS = "grass"
    FISHING = "fishing"