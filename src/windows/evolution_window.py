# This file contains a top level window that will animate
# a Pokemon's evolution

# Imports

import tkinter as tk
from tkinter import messagebox

import math
import random

from src.pokemon.pokemon import Pokemon
from src.pokemon.species import Species
from src.utils.font import get_mono_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define the 'EvolutionWindow' class
class EvolutionWindow(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, a Pokemon and the evolution
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon, evolution: Species):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.pokemon = pokemon
        self.evolution = evolution

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Prompt the user to confirm the evolution
        result = messagebox.askyesno("Evolution", f"Would you like to evolve {self.pokemon.nickname}?")

        # If user clicked no
        if not result:
            return None # Return none

        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Evolve {self.pokemon.nickname}", width=300, height=300)

        # Create an image label for the sprite
        image = tk.Label(self.window, image=self.pokemon.get_sprite("front"))
        image.place(x=150, y=150, anchor=tk.CENTER)

        # Define a recursive to shake the image
        def shake(count, limit, x_direction = 3):
            # Modify the position of the image using the x-coordinate shift
            image.place(x=150 + x_direction, y=150 + random.randint(-1, 1), anchor=tk.CENTER)
            # Increment the counter
            count += 1
            # If we continue
            if not count >= limit:
                # Schedule a recursive shake
                self.window.after(max(1, int((limit - count) * 4)), lambda c=count, l=limit, xd=-x_direction: shake(c, l, xd))

        # Start the recursion chain
        limit = 61
        shake(0, limit)
        # Calculate the total delay
        total_delay = 4 * (limit - 1) * limit // 2

        # Define the evolution complete callback
        def on_evolution_complete():
            # Modify the fields of the Pokemon
            old_name = self.pokemon.nickname
            old_max_health = self.pokemon.get_max_health()
            if self.pokemon.nickname.lower() == self.pokemon.species:
                # Update nickname to match new species name
                self.pokemon.nickname = self.evolution.name.title()
            self.pokemon.species = self.evolution.name
            # Calculate the health ratio
            health_ratio = self.pokemon.get_health() / old_max_health
            # Calculate the adjusted health
            adj_health = math.ceil(self.pokemon.get_max_health() * health_ratio)
            self.pokemon.condition.health = adj_health
            # Change the image label
            image.config(image=self.pokemon.get_sprite("front"))
            # Create a label to show the evolution state
            evo_label = tk.Label(self.window, text=f"{old_name} has evolved into {self.pokemon.species.title()}",
                                 font=get_mono_font(), wraplength=280, padx=10, pady=10)
            evo_label.place(rely=0.8, relx=0.5, anchor=tk.CENTER)
            # Add a close button
            close_button = tk.Button(self.window, text="Close", command=self.window.destroy, width=10, height=2,
                                     bd=3, relief=tk.GROOVE)
            close_button.place(rely=0.2, relx=0.5, anchor=tk.CENTER)

        # Schedule the evolution callback
        self.window.after(total_delay + 500, on_evolution_complete)

        # Return an instance of self
        return self