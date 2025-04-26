from typing import TypedDict

class StatTable(TypedDict):
    health: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class OptionalStatTable(TypedDict, total=False):
    health: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int