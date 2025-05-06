# This file is responsible for loading raw pack JSON files and
# converting them

import json

from src.pokemon.species import Species
from src.pokemon.move import Move

class LoadedPack:
    def __init__(
            self,
            species: list[Species],
            moves: list[Move]
    ):
        self.species = species
        self.moves = moves

def load_pack(path: str):
    loaded_pack = LoadedPack([])
    with open(path, "r") as f:
        data = json.load(f)
        for species in data["species"]:
            loaded_pack.species.append(Species.from_obj(species))
        for move in data["moves"]:
            loaded_pack.moves.append(Move.from_obj(move))
    return loaded_pack
