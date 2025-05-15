# This file contains a top level window used for selecting a Pokemon to switch into

# Imports

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from src import holder
from src.pokemon.pokemon import Pokemon
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow
from src.resources import type_colors

# Define the 'PokemonSelector' class
class PokemonSelector(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, the current Pokemon,
    # and a callback, and a flat that defines whether this selection screen can be cancelled/closed or not
    def __init__(self, parent: tk.Wm | tk.Misc, current: Pokemon, callback: Callable[[Pokemon], None], cancellable: bool):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.callback = callback
        self.current = current
        self.cancellable = cancellable

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Select a Pokemon", width=550, height=400)

        # Create a container frame
        container = tk.Frame(self.window)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Retrieve the current save
        save = holder.save

        # Define a callback to handle Pokemon selection
        def on_select(selection: Pokemon):
            # Call the callback function
            self.callback(selection)
            # Destroy the window
            self.window.destroy()

        # Iterate each Pokemon in the player's team, enumerated
        for i, pokemon in enumerate(save.team):
            # Define variables
            row = i // 3
            col = i % 3
            color = type_colors[pokemon.get_species().types[0]]

            # Check if Pokemon is conscious
            if pokemon.condition.health <= 0:
                # Change color to gray
                color = "#6b6b6b"

            # Create a frame for the Pokemon
            frame = tk.Frame(container, bg=color, width=150, padx=20, pady=10, relief=tk.GROOVE, bd=3)
            frame.grid(row=row, column=col, padx=5, pady=5)

            # Create a label for the Pokemon's sprite
            sprite_label = tk.Label(frame, image=pokemon.get_sprite("front"), bg=color)
            sprite_label.grid(row=0, column=0, rowspan=3)

            # Create a label for the Pokemon's name
            name_label = tk.Label(frame, text=f"{pokemon.nickname}\tLv. {pokemon.level}",
                                  bg=color, anchor=tk.W, width=20)
            name_label.grid(row=0, column=1, sticky=tk.W)

            # Check if Pokemon is shiny
            if pokemon.shiny:
                name_label.config(text=f"✨ {name_label.cget('text')}")

            # Define dimensions
            width = 148
            height = 15

            # Create health bar frame
            health_frame = tk.Frame(
                frame,
                bd=1,
                relief=tk.SUNKEN,
                width=width,
                height=height
            )
            health_frame.grid(row=1, column=1, sticky="w")
            health_frame.grid_propagate(False)

            # Calculate health percentage
            health_percentage = pokemon.get_health() / pokemon.get_max_health()
            # Determine appropriate color for the health bar
            health_color = "#00CC00" if health_percentage > 0.5 else "#FFCC00" if health_percentage > 0.2 else "#FF0000"

            # Create health bar canvas
            health_bar = tk.Canvas(
                health_frame,
                width=width,
                height=height,
                bg="white",
                highlightthickness=0
            )
            health_bar.pack()

            # Draw the health bar
            health_bar.create_rectangle(0, 0, width * health_percentage, height, fill=health_color, outline="")

            # Add a select button
            select_button = tk.Button(frame, text="Select", relief=tk.GROOVE, width=20,
                                      command=lambda pkm=pokemon: on_select(pkm))
            select_button.grid(row=2, column=1)

            # Check if Pokemon is not healthy
            if pokemon.condition.health <= 0 or pokemon == self.current:
                # Disable selection button
                select_button.config(state=tk.DISABLED)

        # If this selection is cancellable
        if self.cancellable:
            cancel_button = tk.Button(container, text="CANCEL", padx=10, pady=10, bd=3,
                                      relief=tk.GROOVE, width=73, font=get_bold_font(), command=self.window.destroy)
            cancel_button.grid(row=2, column=0, columnspan=2)
        else:
            # Define an on destroy callback
            def on_destroy():
                messagebox.showerror("Select a Pokemon", "You must select a Pokemon!")
                return # Exit

            # Attach to the WM_DESTROY_WINDOW event
            self.window.protocol("WM_DELETE_WINDOW", on_destroy)

        # Return an instance of self
        return self