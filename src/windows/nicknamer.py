# This file contains a top level window for assigning nicknames to
# newly caught Pokemon.

# Imports

import tkinter as tk

from src.pokemon.pokemon import Pokemon
from src.windows.abstract.top_level_window import TopLevelWindow

# Define the 'Nicknamer' class
# The structure of this Top Level Window class differs from that of others
# because this one is primarily supposed to take a value (a Pokemon), assign
# a nickname, then self-destruct
class Nicknamer(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root and an instance of a Pokemon
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)
        # Initialize fields
        self.pokemon = pokemon

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Select a Nickname", width=300, height=140)
        # Create a container frame
        frame = tk.Frame(self.window)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Create an image for the Pokemon
        sprite = tk.Label(frame, image=self.pokemon.get_sprite("front"))
        sprite.grid(row=0, column=0, rowspan=2)

        # Create a species label
        species_label = tk.Label(frame, text=f"{self.pokemon.species.title()} Lv. {self.pokemon.level}", anchor=tk.W)
        species_label.grid(row=0, column=1, sticky=tk.EW, pady=(10, 0))

        # Create a nickname variable
        nickname_var = tk.StringVar(value=self.pokemon.nickname)

        # Create a nickname entry
        nickname_entry = tk.Entry(frame, textvariable=nickname_var, justify=tk.LEFT)
        nickname_entry.grid(row=1, column=1, sticky=tk.EW, pady=(0, 10))

        # Define the continue button callback
        def callback():
            # Apply the username
            self.pokemon.nickname = nickname_var.get()
            # Destroy the window
            self.window.destroy()

        # Create a continue button using the callback
        continue_button = tk.Button(frame, text="Continue", relief=tk.GROOVE, command=callback)
        continue_button.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        # Return an instance of self
        return self

    # Define a static method named 'prompt_nickname' that takes a Pokemon
    # and creates a top level window that prompts the user to set a nickname
    @staticmethod
    def prompt_nickname(parent: tk.Wm | tk.Misc, pokemon: Pokemon):
        # Create an instance of 'Nicknamer'
        Nicknamer(parent, pokemon).draw().wait()