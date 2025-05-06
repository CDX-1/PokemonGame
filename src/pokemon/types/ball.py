# This file defines three classes: CatchContext, BallHandler, Ball

# CatchContext is a metadata class that is used when performing
# calculations to determine whether a Pokeball is successful or not.

# The BallHandler class is a functional class meaning it just contains
# a callback function that will be called whenever a certain ball type is
# used.

# The Ball class is an enum that contains every implemented ball type, and
# it's respective handler.

# Imports

from enum import Enum
from typing import Callable

from src.pokemon.pokemon import Pokemon
from src.pokemon.types.encounter_type import EncounterType

# Define CatchContext class

class CatchContext:
    def __init__(
            self,
            pokemon: Pokemon, # The players current Pokemon
            wild_pokemon: Pokemon, # The wild Pokemon/encounter Pokemon
            encounter_type: EncounterType, # The type of encounter (grass, fishing)
            turn: int # the turn of battle
    ):
        # Initialize fields
        self.pokemon = pokemon
        self.wild_pokemon = wild_pokemon
        self.encounter_type = encounter_type
        self.turn = turn

# Define BallHandler class

class BallHandler:
    # Wraps a callback function that takes in a catch context and returns the ball's catch rate modifier
    def __init__(self, handler: Callable[[CatchContext], float]):
        # Initialize fields
        self.handler = handler

# Define Ball class

class Ball(Enum):
    POKE_BALL = BallHandler(lambda ctx: 1) # Standard Pokeball, x1
    GREAT_BALL = BallHandler(lambda ctx: 1.5) # Better Pokeball, x1.5
    ULTRA_BALL = BallHandler(lambda ctx: 2) # Good Pokeball, x2
    MASTER_BALL = BallHandler(lambda ctx: 255) # Perfect Pokeball, x255 (100% catch rate)
    QUICK_BALL = BallHandler(lambda ctx: 5 if ctx.turn == 1 else 1) # Quick Ball, x5 on turn 1, otherwise x1