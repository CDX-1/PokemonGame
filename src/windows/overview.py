# This file defines a top level window that shows detailed information
# about a specific caught Pokemon

# Imports

import tkinter as tk

from src import holder
from src.pokemon.move import Move
from src.pokemon.pokemon import Pokemon
from src.pokemon.types.stat import Stat
from src.utils import images
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow
from src.windows.move_swapper import MoveSwapper


# Define the 'Overview' class
class Overview(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root and a Pokemon
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)
        # Initialize fields
        self.pokemon = pokemon

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Define 'pkm' as a shorthand for self.pokemon
        pkm = self.pokemon
        # Define 'species' as a shorthand for self.pokemon.get_species
        species = self.pokemon.get_species()

        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Save Creator", width=600, height=500)
        # Create a container frame
        frame = TopLevelWindow.create_basic_frame(self.window)

        # Create a label for the Pokemon sprite
        sprite_label = tk.Label(frame, image=pkm.get_sprite("front"))
        sprite_label.grid(row=0, column=0, rowspan=3)

        # Create a nickname label
        nickname_label = tk.Label(frame, text=pkm.nickname, anchor=tk.W)
        nickname_label.grid(row=0, column=1, columnspan=3, sticky=tk.W)

        # Check if Pokemon is shiny
        if pkm.shiny:
            nickname_label.config(text=f"{pkm.nickname}  ✨")

        # Create a species label
        species_label = tk.Label(frame, text=f"{species.name.title()}  |  {species.genus.title()}", anchor=tk.W)
        species_label.grid(row=1, column=1, sticky=tk.W)

        # Create a frame to contain the types
        types_frame = tk.Frame(frame)
        types_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W)

        # Iterate the Pokemon's types, enumerated
        for i, pokemon_type in enumerate(species.types):
            # Create a frame for the type
            type_frame = tk.Frame(types_frame)
            type_frame.grid(row=0, column=i)
            # Add an image label for the type icon
            icon_label = tk.Label(type_frame, image=images.get_image(pokemon_type))
            icon_label.grid(row=0, column=0)
            # Add a text label for the type name
            type_label = tk.Label(type_frame, text=pokemon_type.title())
            type_label.grid(row=0, column=1)

        # Add a flavour header
        flavour_header = tk.Label(frame, text="About", font=get_bold_font(), anchor=tk.W)
        flavour_header.grid(row=3, column=0, columnspan=4, sticky=tk.EW)

        # Add a flavour label
        flavour_label = tk.Label(frame, text=species.desc.replace("\n", " "), justify=tk.LEFT, anchor=tk.W, wraplength=350)
        flavour_label.grid(row=4, column=0, columnspan=4, sticky=tk.EW)

        # Creating a table for stats

        stats_frame = tk.Frame(frame)
        stats_frame.grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        # Add a stats table header
        stats_header = tk.Label(stats_frame, text="Stats", anchor=tk.W, font=get_bold_font())
        stats_header.grid(row=6, column=0, columnspan=2, sticky=tk.W)

        # Add a individual value (IV) table header
        ivs_header = tk.Label(stats_frame, text="IVs", anchor=tk.W, font=get_bold_font())
        ivs_header.grid(row=6, column=2, columnspan=2, sticky=tk.W)

        # Add an effort value (EV) table header
        evs_header = tk.Label(stats_frame, text="EVs", anchor=tk.W, font=get_bold_font())
        evs_header.grid(row=6, column=4, columnspan=2, sticky=tk.W)

        # Iterate each stat, enumerated
        for i, stat in enumerate(Stat):
            # Create a stat prefix label
            stat_prefix = tk.Label(stats_frame, text=f"{stat.format()}:", anchor=tk.W)
            stat_prefix.grid(row=7 + i, column=0, sticky=tk.W)
            # Create a stat value label
            stat_value = tk.Label(stats_frame, text=pkm.get_stat(stat), anchor=tk.W)
            stat_value.grid(row=7 + i, column=1, sticky=tk.W, padx=(0, 20))

            # Create a IV prefix label
            iv_prefix = tk.Label(stats_frame, text=f"{stat.format()}:", anchor=tk.W)
            iv_prefix.grid(row=7 + i, column=2, sticky=tk.W)
            # Create a IV value label
            iv_value = tk.Label(stats_frame, text=pkm.ivs[stat.value], anchor=tk.W)
            iv_value.grid(row=7 + i, column=3, sticky=tk.W, padx=(0, 20))

            # Create a EV prefix label
            ev_prefix = tk.Label(stats_frame, text=f"{stat.format()}:", anchor=tk.W)
            ev_prefix.grid(row=7 + i, column=4, sticky=tk.W)
            # Create a EV value label
            ev_prefix = tk.Label(stats_frame, text=pkm.evs[stat.value], anchor=tk.W)
            ev_prefix.grid(row=7 + i, column=6, sticky=tk.W, padx=(0, 20))

        # Create a header frame for all the move headers
        header_frame = tk.Frame(frame)
        header_frame.grid(row=9, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        # Create a header label for the Pokemon's type name
        type_header = tk.Label(header_frame, text="Type", anchor=tk.W, font=get_bold_font(), width=4)
        type_header.grid(row=0, column=0, sticky=tk.W)

        # Create a header label for the Pokemon's moves name
        move_header = tk.Label(header_frame, text="Move", anchor=tk.W, font=get_bold_font(), width=10)
        move_header.grid(row=0, column=1, sticky=tk.W)

        # Create a header label for the Pokemon's moves power
        move_header = tk.Label(header_frame, text="Pow.", anchor=tk.W, font=get_bold_font(), width=5)
        move_header.grid(row=0, column=2, sticky=tk.W)

        # Create a header label for the Pokemon's moves accuracy
        accuracy_header = tk.Label(header_frame, text="Acc.", anchor=tk.W, font=get_bold_font(), width=5)
        accuracy_header.grid(row=0, column=3, sticky=tk.W)

        # Create a header label for the Pokemon's moves description
        desc_header = tk.Label(header_frame, text="Desc.", anchor=tk.W, font=get_bold_font(), width=25)
        desc_header.grid(row=0, column=4, sticky=tk.W)

        # Create a header label for swapping the Pokemon's moves
        swap_header = tk.Label(header_frame, text="Swap", anchor=tk.W, font=get_bold_font())
        swap_header.grid(row=0, column=5, sticky=tk.W)

        # Iterate each move, enumerated
        for i, move_obj in enumerate(pkm.condition.move_set):
            # Retrieve move object
            move = holder.get_move(move_obj.name)
            # Create a frame for the move data
            move_frame = tk.Frame(frame)
            move_frame.grid(row=10 + i, column=0, columnspan=4, sticky=tk.W)
            # Create a label for the move type
            type_label = tk.Label(move_frame, image=images.get_image(move.type), anchor=tk.CENTER, width=38)
            type_label.grid(row=i, column=0)
            # Create a label for the move name
            move_label = tk.Label(move_frame, text=move.format(), anchor=tk.W, width=10)
            move_label.grid(row=i, column=1, sticky=tk.W)
            # Create a label for the move power
            power_label = tk.Label(move_frame, text=move.power, anchor=tk.W, width=5)
            power_label.grid(row=i, column=2, sticky=tk.W)
            # Create a label for the move accuracy
            accuracy_label = tk.Label(move_frame, text=f"{move.accuracy}%", anchor=tk.W, width=5)
            accuracy_label.grid(row=i, column=3, sticky=tk.W)
            # Create a label for the move description
            description_label = tk.Label(move_frame, text=move.desc.replace("\n", " "), anchor=tk.W,
                                         wraplength=250, justify=tk.LEFT, width=25)
            description_label.grid(row=i, column=4, sticky=tk.W)

            # Define a callback function to handle swapping
            def callback(selected_move: Move):
                # Create and open the move swapper for the selected move
                MoveSwapper(self.parent, pkm, selected_move).draw().wait()

            # Create a label for the swap button
            swap_label = tk.Label(move_frame, image=images.get_image("swap", (30, 30)), anchor=tk.W)
            swap_label.grid(row=i, column=5, sticky=tk.W)

            # Bind swap callback to swap label
            swap_label.bind("<Button-1>", lambda event, selected_move=move: callback(selected_move))

        # Return an instance of self
        return self