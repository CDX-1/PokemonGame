# This file provides several functions to allow other modules to access
# content/data such as Pokemon species, moves, items, etc.

# Imports

import tkinter as tk

from src.game.battle_client import BattleClient
from src.game.save import Save
from src.pack_processor import LoadedPack
from src.pokemon.move import Move

from src.pokemon.species import Species

# Initialize the root variable for later access
root: tk.Tk | None

# Initialize the 'pack' variable which will be updated to a loaded pack
# by the main module so that pack data can be queried later
pack: LoadedPack | None = None

# Initialize the 'save' variable which will be updated to a loaded save
# by the main menu so that other modules can access the current save
save: Save | None = None

# Initialize the 'battle' variable which will be updated to any ongoing
# battle that the player is in
battle: BattleClient | None = None

# Define the 'get_species' function that takes a species name and returns
# a species object
def get_species(species_name: str) -> Species:
    # Filter pack species that match the species_name
    filtered = list(filter(lambda entry: entry.name == species_name, pack.species))
    # Check if filtered list is empty
    if len(filtered) == 0:
        # Raise a KeyError to indicate an invalid species name
        raise KeyError("Invalid species: " + species_name)
    # Return the first matching species
    return filtered[0]

# Define the 'get_move' function that takes a move name and returns
# a move object
def get_move(move_name: str) -> Move:
    # Filter pack move that match the move
    filtered = list(filter(lambda entry: entry.name == move_name, pack.moves))
    # Check if filtered list is empty
    if len(filtered) == 0:
        # Raise a KeyError to indicate an invalid move name
        raise KeyError("Invalid move: " + move_name)
    # Return the first matching move
    return filtered[0]