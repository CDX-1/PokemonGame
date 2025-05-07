# CatchContext is a metadata class that is used when performing
# calculations to determine whether a Pokeball is successful or not.

# Imports

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