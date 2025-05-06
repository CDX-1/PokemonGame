# This file defines several dictionaries with specific keys and types (TypedDicts)
# that represent a Pokemon's stat distribution in various scenarios.

# Imports

from typing import TypedDict

# Classical stat table, used to represent a Pokemon's base stats

class StatTable(TypedDict):
    health: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

# A stat table where the values are optional, this is used in scenarios
# where you don't need to specify a value for every stat such as an effort
# value (EV) yield.

class OptionalStatTable(TypedDict, total=False):
    health: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

# A stat table that is specifically for battle and represents stat changes that
# occurred during battle and adds volatile stats such as accuracy and evasion.

class BattleStatTable(TypedDict, total=False):
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    accuracy: int
    evasion: int