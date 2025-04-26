from __future__ import annotations

from enum import Enum

class Stat(Enum):
    HP = "hp"
    ATTACK = "attack"
    SPECIAL_ATTACK = "special_attack"
    DEFENSE = "defense"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"

    @staticmethod
    def of(text: str) -> Stat:
        for stat in Stat:
            if stat.name.lower() == text or stat.value.lower() == text.lower():
                return stat
        raise KeyError("Invalid stat: " + text)