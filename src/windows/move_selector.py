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
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD"
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

        # Iterate Pokemon's move set, enumerated
        for i, battle_move in enumerate(self.pokemon.condition.move_set):
            row = i // 2
            col = i % 2

            # Retrieve move object
            move = holder.get_move(battle_move.name)

            # Create a frame for the move
            move_frame = tk.Frame(frame, padx=10, pady=10, bg=type_colors[move.type])
            move_frame.grid(row=row, column=col, padx=5, pady=5)

            # Add the type icon of the move
            type_label = tk.Label(move_frame, image=images.get_image(move.type), bg=type_colors[move.type])
            type_label.grid(row=0, column=0, padx=(0, 5))

            # Add the name of the move
            move_name = " ".join(move.name.split("_")).title()
            move_label = tk.Label(move_frame, text=move_name, font=get_bold_font(), bg=type_colors[move.type])
            move_label.grid(row=0, column=1, padx=(0, 10))

            # Add the PP label
            pp_label = tk.Label(move_frame, text=f"{battle_move.pp}/{battle_move.max_pp}", bg=type_colors[move.type])
            pp_label.grid(row=0, column=2)

            # Center contents within their cell
            move_frame.grid_columnconfigure(0, weight=1)
            move_frame.grid_columnconfigure(1, weight=1)
            move_frame.grid_columnconfigure(2, weight=1)

            # Add click bindings to all widgets
            move_frame.bind("<Button-1>", lambda e, name=battle_move.name: self.on_move_click(name))
            type_label.bind("<Button-1>", lambda e, name=battle_move.name: self.on_move_click(name))
            move_label.bind("<Button-1>", lambda e, name=battle_move.name: self.on_move_click(name))
            pp_label.bind("<Button-1>", lambda e, name=battle_move.name: self.on_move_click(name))

        # Add a cancel button
        cancel_button = tk.Button(frame, text="CANCEL", font=get_bold_font(), width=40, relief=tk.GROOVE, bg="#ececec",
                                  command=lambda: self.window.destroy())
        cancel_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Center the grid in the frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Return an instance of self
        return self

    # Define the move click callback
    def on_move_click(self, move_name: str):
        # Destroy the window
        self.window.destroy()
        # Call the callback
        self.callback(move_name)