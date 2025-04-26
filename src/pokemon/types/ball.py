from __future__ import annotations

from enum import Enum
from typing import Callable

from src.pokemon.pokemon import Pokemon
from src.pokemon.types.encounter_type import EncounterType

class CatchContext:
    def __init__(
            self,
            pokemon: Pokemon,
            wild_pokemon: Pokemon,
            encounter_type: EncounterType,
            turn: int
    ):
        self.pokemon = pokemon
        self.wild_pokemon = wild_pokemon
        self.encounter_type = encounter_type
        self.turn = turn

class BallHandler:
    def __init__(self, handler: Callable[[CatchContext], float]):
        self.handler = handler

class Ball(Enum):
    POKE_BALL = BallHandler(lambda ctx: 1)
    GREAT_BALL = BallHandler(lambda ctx: 1.5)
    ULTRA_BALL = BallHandler(lambda ctx: 2)
    MASTER_BALL = BallHandler(lambda ctx: 255)
    QUICK_BALL = BallHandler(lambda ctx: 5 if ctx.turn == 1 else 1)