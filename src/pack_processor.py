# This file is responsible for loading raw pack JSON files and
# converting them into flexibly usable Python objects.

# Imports

import json

from src.pokemon.species import Species
from src.pokemon.move import Move

# Define 'LoadedPack' class to represent a loaded pack
class LoadedPack:
    def __init__(
            self,
            species: list[Species], # A list of the species the pack contains
            moves: list[Move] # A list of the moves the pack contains
    ):
        # Initialize fields
        self.species = species
        self.moves = moves

# Define 'load_pack' function that takes a file path and loads the pack at that file
def load_pack(path: str):
    # Initialize the LoadedPack with two empty species and moves lists
    loaded_pack = LoadedPack([], [])
    # Open the file at the path in read (R) mode with the file referenced as 'f'
    with open(path, "r") as f:
        # Load the data from the file from JSON format into a Python dictionary
        data = json.load(f)
        # Iterate all the species in the dictionary
        for species in data["species"]:
            # Append the species object cast into the species class to the species list
            loaded_pack.species.append(Species.from_obj(species))
        # Iterate all the moves in the dictionary
        for move in data["moves"]:
            # Append the move object cast into the move class to the moves list
            loaded_pack.moves.append(Move.from_obj(move))
    # Return the loaded pack
    return loaded_pack
