# This file defines a top level window that is used to select
# a move that will replace another move in a Pokemon's moveset

# Imports

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Callable

from src import holder
from src.pokemon.move import Move
from src.pokemon.pokemon import Pokemon
from src.pokemon.types.battle_condition import BattleMove
from src.utils import images
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define the 'MoveSwapper' class
class MoveSwapper(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, a Pokemon, a move, and a callback
    def __init__(self, parent: tk.Wm | tk.Misc, pokemon: Pokemon, move: Move, callback: Callable[[], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)
        # Initialize fields
        self.pokemon = pokemon
        self.move = move
        self.callback = callback

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Define 'pkm' as a shorthand for self.pokemon
        pkm = self.pokemon
        # Define 'species' as a shorthand for self.pokemon.get_species()
        species = self.pokemon.get_species()
        # Define 'mv' as a shorthand for self.move
        mv = self.move

        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Replace {mv.format()}", width=550, height=400)
        # Create a container frame
        frame = TopLevelWindow.create_basic_frame(self.window)

        # Create a canvas for scrolling
        canvas = tk.Canvas(frame)
        # Create a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        # Create a scrollable frame inside the canvas
        scrollable_frame = tk.Frame(canvas)

        # Configure the canvas to use the scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create a window inside the canvas with the scrollable frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a header label
        title_label = tk.Label(scrollable_frame, text=f"Select a move to replace for {mv.format().upper()}:")
        title_label.grid(row=0, column=0, columnspan=5)

        # Define the Pokemon's move set
        move_set = pkm.get_moves()

        # Initialize an array of learnable moves
        moves = []

        # Iterate all learnt moves
        for move in species.get_known_moves(pkm.level):
            # Check if move is not already in move set
            if not move in move_set:
                # Add move to moves list
                moves.append(move)

        # Iterate all tutor and machine moves
        for move in pkm.tutor_machine_moves:
            # Check if move is not already in move set
            if not move in move_set:
                # Add move to moves list
                moves.append(move)

        # Create a header frame for all the move headers
        header_frame = tk.Frame(scrollable_frame)
        header_frame.grid(row=1, column=0, columnspan=5, sticky=tk.W, pady=(10, 0))

        # Create a header label for the move's type name
        type_header = tk.Label(header_frame, text="Type", anchor=tk.W, font=get_bold_font(), width=4)
        type_header.grid(row=0, column=0, sticky=tk.W)

        # Create a header label for the move's category name
        category_header = tk.Label(header_frame, text="Cat.", anchor=tk.W, font=get_bold_font(), width=5)
        category_header.grid(row=0, column=1, sticky=tk.W)

        # Create a header label for the move's moves name
        move_header = tk.Label(header_frame, text="Move", anchor=tk.W, font=get_bold_font(), width=15)
        move_header.grid(row=0, column=2, sticky=tk.W)

        # Create a header label for the move's moves power
        move_header = tk.Label(header_frame, text="Pow.", anchor=tk.W, font=get_bold_font(), width=5)
        move_header.grid(row=0, column=3, sticky=tk.W)

        # Create a header label for the move's moves accuracy
        accuracy_header = tk.Label(header_frame, text="Acc.", anchor=tk.W, font=get_bold_font(), width=5)
        accuracy_header.grid(row=0, column=4, sticky=tk.W)

        # Create a header label for the move's moves description
        desc_header = tk.Label(header_frame, text="Desc.", anchor=tk.W, font=get_bold_font(), width=25)
        desc_header.grid(row=0, column=5, sticky=tk.W)

        # Create a callback function to handle the move being selected
        def callback(confirmed_move):
            # Retrieve Pokemon's current move set
            current_moves = pkm.get_moves()
            # Ensure no data has updated since this window has updated
            if not confirmed_move in current_moves and mv.name in current_moves:
                # Retrieve object of the confirmed move
                confirmed_move_obj = holder.get_move(confirmed_move)
                # Retrieve the move index in the move set array
                move_index = pkm.condition.move_set.index(list(filter(lambda entry: entry.name == mv.name, pkm.condition.move_set))[0])
                # Create an instance of a 'BattleMove'
                battle_move = BattleMove(
                    confirmed_move,
                    confirmed_move_obj.pp,
                    confirmed_move_obj.pp,
                    False
                )
                # Swap the move set with new battle move in the old index
                pkm.condition.move_set[move_index] = battle_move
            else:
                # Notify user that the move could not be learnt
                messagebox.showerror("Failed to Teach Move", f"Failed to teach {pkm.nickname} the move, {mv.format()}")
            # Destroy window
            self.window.destroy()
            # Call the callback function
            self.callback()

        # Create a header label for the Pokemon's moves confirm button
        confirm_header = tk.Label(header_frame, text="Confirm", anchor=tk.W, font=get_bold_font(), width=25)
        confirm_header.grid(row=0, column=6, sticky=tk.W)

        # Iterate all the learnable moves, enumerated
        for i, move_name in enumerate(moves):
            # Retrieve instance of actual move
            move = holder.get_move(move_name)

            # Create a frame for the move data
            move_frame = tk.Frame(scrollable_frame)
            move_frame.grid(row=i + 2, column=0, columnspan=5, sticky=tk.W)

            # Create a label for the move type
            type_label = tk.Label(move_frame, image=images.get_image(move.type), anchor=tk.CENTER, width=30)
            type_label.grid(row=i, column=0)

            # Create a label for the move category
            category_label = tk.Label(move_frame, text=move.damage_class.format(), anchor=tk.W, width=5)
            category_label.grid(row=i, column=1, sticky=tk.W)

            # Create a label for the move name
            move_label = tk.Label(move_frame, text=move.format(), anchor=tk.W, width=15)
            move_label.grid(row=i, column=2, sticky=tk.W)

            # Create a label for the move power
            power_label = tk.Label(move_frame, text=move.power, anchor=tk.W, width=5)
            power_label.grid(row=i, column=3, sticky=tk.W)

            # Create a label for the move accuracy
            accuracy_label = tk.Label(move_frame, text=f"{move.accuracy}%", anchor=tk.W, width=5)
            accuracy_label.grid(row=i, column=4, sticky=tk.W)

            # Create a label for the move description
            description_label = tk.Label(move_frame, text=move.desc.replace("\n", " "), anchor=tk.W,
                                         wraplength=170, justify=tk.LEFT, width=25)
            description_label.grid(row=i, column=5, sticky=tk.W)

            # Create a button for confirming the move
            confirm_button = tk.Button(move_frame, text="Confirm", anchor=tk.W, relief=tk.GROOVE, command=lambda confirmed_move=move_name: callback(confirmed_move))
            confirm_button.grid(row=i, column=6, sticky=tk.W)

        # Configure scrolling with mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind mousewheel event to the canvas
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Return an instance of self
        return self