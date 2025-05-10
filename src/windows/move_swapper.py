# This file defines a top level window that is used to select
# a move that will replace another move in a Pokemon's moveset

# Imports

import tkinter as tk

from src.pokemon.move import Move
from src.pokemon.pokemon import Pokemon
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define the 'MoveSwapper' class
class MoveSwapper(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, a Pokemon, and a move
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon, move: Move):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)
        # Initialize fields
        self.pokemon = pokemon
        self.move = move

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Define 'mv' as a shorthand for self.move
        mv = self.move

        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Save Creator", width=300, height=400)
        # Create a container frame
        frame = TopLevelWindow.create_basic_frame(self.window)

        # Create a header frame
        header_frame = tk.Frame(frame)
        header_frame.pack()

        # Create a header label
        header_label = tk.Label(header_frame, text=f"Select a move to replace for")
        header_label.grid(row=0, column=0)

        # Create a header label that shows the move name in a different font
        header_label = tk.Label(header_frame, text=mv.format(), font=get_bold_font())
        header_label.grid(row=0, column=1)

        # Return an instance of self
        return self