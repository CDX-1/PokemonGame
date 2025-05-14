# This file contains a top level window used for selecting
# the move which will be used

# Imports

import tkinter as tk
from typing import Callable

from src import holder
from src.pokemon.pokemon import Pokemon
from src.utils import images
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define a type-colour map which binds every Pokemon type to a hex code
type_colors = {
    "Normal": "#A8A77A",
    "Fire": "#EE8130",
    "Water": "#6390F0",
    "Electric": "#F7D02C",
    "Grass": "#7AC74C",
    "Ice": "#96D9D6",
    "Fighting": "#C22E28",
    "Poison": "#A33EA1",
    "Ground": "#E2BF65",
    "Flying": "#A98FF3",
    "Psychic": "#F95587",
    "Bug": "#A6B91A",
    "Rock": "#B6A136",
    "Ghost": "#735797",
    "Dragon": "#6F35FC",
    "Dark": "#705746",
    "Steel": "#B7B7CE",
    "Fairy": "#D685AD"
}

# Define the 'MoveSelector' class
class MoveSelector(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, a Pokemon, and a ready callback
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon, callback: Callable[[str], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.pokemon = pokemon
        self.callback = callback

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Select a Move", width=400, height=300)

        # Create a container frame
        frame = tk.Frame(self.window)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Iterate Pokemon's move set
        for battle_move in self.pokemon.condition.move_set:
            # Retrieve move object
            move = holder.get_move(battle_move.name)

            # Create a frame for the move
            move_frame = tk.Frame(frame, width=20, padx=5, pady=5)
            move_frame.grid(row=0, column=0, sticky=tk.CENTER)

            # Add the type icon of the move
            type_label = tk.Label(move_frame, image=images.get_image(move.type), anchor=tk.CENTER)
            type_label.grid(row=0, column=0, sticky=tk.CENTER)

            # Add the name of the move
            move_label = tk.Label(move_frame, text=move.name, anchor=tk.CENTER)
            move_label.grid(row=0, column=1, sticky=tk.CENTER)

            # Add the PP label
            pp_label = tk.Label(move_frame, text=f"{battle_move.pp}/{battle_move.max_pp}", anchor=tk.CENTER)
            pp_label.grid(row=0, column=2, sticky=tk.CENTER)

        # Return an instance of self
        return self