# This file contains the code for the Navigator which is containerized in
# a Tkinter frame to be embedded in the root window that contains a route map
# and navigation buttons

# Imports

# This is used to allow the 'Navigator' class to return itself in its methods/functions
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from src import holder
from src.game.battle_client import BattleClient
from src.routes import get_encounter
from src.pokemon.types.stat import Stat
from src.utils import images
from src.utils.font import get_mono_font, get_title_font
from src.windows.bag_window import BagWindow
from src.windows.battle_window import BattleWindow
from src.windows.overview import Overview
from src.windows.shop_window import ShopWindow

# Define the 'Navigator' class
class Navigator:
    # Class constructor method takes a 'parent' element such as the Tkinter root
    def __init__(self, parent: tk.Wm | tk.Misc):
        # Initialize fields
        self.parent = parent
        # A blank variable that will contain an instance of our frame
        self.frame: tk.Frame | None = None

    # Define the 'draw' method that will create the frame and returns an instance of its
    # self so that the 'factory' API architecture can be used (method-chaining)
    def draw(self) -> Navigator:
        # Check if the frame is not none
        if self.frame is not None:
            self.frame.destroy() # Destroy the frame

        # Initialize the frame
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Retrieve the current save
        save = holder.save

        # Create a centered frame to contain team sprites
        team_frame = tk.Frame(self.frame)
        team_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Define a function to draw the team to the frame
        def draw_team_frame():
            # Iterate all child widgets of 'team_frame'
            for widget in team_frame.winfo_children():
                # Destroy the widget
                widget.destroy()

            # Iterate player's team, enumerated
            for i, pokemon in enumerate(save.team):
                # Create a callback function that will open a top level
                # window that shows more details about a Pokemon
                def lookup_callback(event, target):
                    # Create an instance of the Overview window
                    Overview(self.parent, target).draw().wait()

                # Create frame to Pokemon contain details
                frame = tk.Frame(team_frame)
                frame.grid(row=0, column=i, padx=5)

                # Create a label for the sprite
                sprite_label = tk.Label(frame, image=pokemon.get_sprite("front"))
                sprite_label.grid(row=0, column=0)

                # Bind the lookup callback to the sprite
                sprite_label.bind("<Button-1>", lambda event, pkm=pokemon: lookup_callback(event, pkm))

                # Create a frame for the species header
                header = tk.Frame(frame)
                header.grid(row=1, column=0)

                # Add a label for the Pokemon's nickname
                nickname_label = tk.Label(header, text=pokemon.nickname)
                nickname_label.grid(row=0, column=0)

                # Check if Pokemon is shiny and not an egg
                if pokemon.shiny and not pokemon.egg:
                    # Change text color to gold
                    nickname_label.config(fg="#d3b349")

                # Iterate Pokemon's types, enumerated
                for j, pokemon_type in enumerate(pokemon.get_species().types):
                    # Create type label
                    type_label = tk.Label(header, image=images.get_image(pokemon_type))
                    type_label.grid(row=0, column=j + 1)

                # Get current experience
                current_exp = pokemon.experience
                # Get total experience needed for next level
                needed_exp = pokemon.get_level_up_experience()
                # Round quotient
                if needed_exp == 0:
                    exp_completion = "0.00"
                else:
                    exp_completion = format((current_exp / needed_exp) * 100, ".2f")

                # Add label for level and experience
                exp_progress_label = tk.Label(frame, text=f"Lv. {pokemon.level} ({exp_completion}%)")
                exp_progress_label.grid(row=2, column=0, pady=(0, 5))

                # Iterate each stat type, enumerated
                for k, stat in enumerate(Stat):
                    # Retrieve stat value
                    stat_value = pokemon.get_stat(stat)
                    # Create a frame for the display
                    stat_frame = tk.Frame(frame)
                    stat_frame.grid(row=k + 3, column=0)
                    # Create a prefix label
                    prefix = tk.Label(stat_frame, text=f"{stat.format()}:")
                    prefix.pack(padx=5, side=tk.LEFT)
                    # Create a stat value label
                    stat_label = tk.Label(stat_frame, text=stat_value)
                    stat_label.pack(padx=5, side=tk.LEFT)
                    # Check if the current stat is HP
                    if stat == Stat.HP:
                        # Update stat value label to be current hp / max hp
                        stat_label.config(text=f"{pokemon.get_health()}/{stat_label.cget('text')}")

        # Call the draw_team_frame function
        draw_team_frame()

        # Initialize variables to calculate positions for widgets below
        width = 700 # Known from main module
        height = 400 # Known from main module
        offset = 30 # Configurable offset
        label_offset = 50 # Configurable offset for keybind label
        scale = (15, 15) # Scaling for the button icons

        # Create a title label
        title = tk.Label(self.frame, text="Pokemon Game", font=get_title_font())
        title.place(x=width / 2, y=offset, anchor=tk.CENTER)

        # Define a function to check if the current window is focused
        def is_focused():
            nonlocal self
            return self.parent.focus_displayof() is not None

        # Define the encounter callback
        def encounter(event):
            # Require that the window be focused
            if not is_focused():
                return # Exit

            # Require that the player not be in a battle
            if holder.battle is not None:
                return # Exit

            # Ensure player has at least one healthy Pokemon
            has_any_health = False # Sentinel value
            for pokemon in save.team:
                if pokemon.condition.health > 0:
                    has_any_health = True
                    break

            if not has_any_health:
                # Tell player to heal their team
                messagebox.showinfo("Can't Battle!", "You must heal your Pokemon first! You can heal " +\
                                    "your Pokemon at the shop!")
                return # Exit

            # Initialize a battle instance
            holder.battle = BattleClient(
                holder.save.team,
                [get_encounter(holder.save.route)],
                False
            )

            # Initialize a battle window
            BattleWindow(self.parent, holder.battle, self.draw).draw().wait()

        # Define the Bag callback
        def bag(event):
            # Initialize the bag window and show it
            BagWindow(self.parent).draw().wait()

        # Define the box callback
        def box(event):
            print("box")

        # Define the shop callback
        def shop(event):
            # Create an instance of the shop window and show it
            ShopWindow(self.parent).draw().wait()

        # Create the encounter button
        encounter_button = tk.Label(self.frame, image=images.get_image("encounter", scale))
        encounter_button.place(x=offset, y=offset, anchor=tk.CENTER)

        # Create the encounter keybind label
        encounter_label = tk.Label(self.frame, text="Z", font=get_mono_font())
        encounter_label.place(x=label_offset, y=label_offset, anchor=tk.CENTER)

        # Add encounter button label bindings
        encounter_button.bind("<Button-1>", encounter)

        # Create the Bag button
        bag_button = tk.Label(self.frame, image=images.get_image("bag", scale))
        bag_button.place(x=width - offset, y=offset, anchor=tk.CENTER)

        # Create the Bag keybind label
        bag_label = tk.Label(self.frame, text="X", font=get_mono_font())
        bag_label.place(x=width - label_offset, y=label_offset, anchor=tk.CENTER)

        # Add Pokemon button label bindings
        bag_button.bind("<Button-1>", bag)

        # Create the box button
        box_button = tk.Label(self.frame, image=images.get_image("box", scale))
        box_button.place(x=offset, y=height - offset, anchor=tk.CENTER)

        # Create the box keybind label
        box_label = tk.Label(self.frame, text="C", font=get_mono_font())
        box_label.place(x=label_offset, y=height - label_offset, anchor=tk.CENTER)

        # Add box button label bindings
        box_button.bind("<Button-1>", box)

        # Create the shop button
        shop_button = tk.Label(self.frame, image=images.get_image("shop", scale))
        shop_button.place(x=width - offset, y=height - offset, anchor=tk.CENTER)

        # Create the shop keybind label
        shop_label = tk.Label(self.frame, text="V", font=get_mono_font())
        shop_label.place(x=width - label_offset, y=height - label_offset, anchor=tk.CENTER)

        # Add shop button label bindings
        shop_button.bind("<Button-1>", shop)

        # Define keybind event callback
        def callback(event):
            # Check the key and call the respective callback
            if event.keysym == "z":
                encounter(event)
            elif event.keysym == "x":
                bag(event)
            elif event.keysym == "c":
                box(event)
            elif event.keysym == "v":
                shop(event)

        # Add keybind bindings
        self.parent.bind("<Key>", callback)

        # Return an instance of self
        return self