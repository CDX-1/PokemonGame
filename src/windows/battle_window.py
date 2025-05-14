# This file defines a window that serves as the visual representation
# of a Pokemon battle
# Imports

import tkinter as tk
from tkinter import messagebox
from typing import Callable
import time

from src import holder
from src.game.battle_client import BattleClient, BattleEvent
from src.pokemon.pokemon import Pokemon
from src.pokemon.types.ball import Ball
from src.utils import images
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow
from src.windows.item_selector import ItemSelector
from src.windows.move_selector import MoveSelector

# Define the 'BattleWindow' class
class BattleWindow(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root and a Battle object
    def __init__(self, parent: tk.Wm | tk.Misc, battle: BattleClient):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.battle = battle

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Battle", width=400, height=300)

        # Initialize widgets
        current_pokemon_image: tk.Label | None = None
        current_opponent_image: tk.Label | None = None

        current_pokemon_label: tk.Label | None = None
        current_opponent_label: tk.Label | None = None

        poke_ball_image: tk.Label | None = None
        poke_ball_original_x: int = 0  # Store the original x position

        last_catch_attempt: int = 0

        # Create a battle frame
        battle_frame = tk.Frame(self.window)
        battle_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Define current pokemon update event callback
        def on_current_pokemon_update(current: Pokemon, opponent: Pokemon):
            # Declare nonlocal variables
            nonlocal current_pokemon_image, current_opponent_image, current_pokemon_label, current_opponent_label

            # Destroy Pokemon label or Opponent label if existing
            for widget in [current_pokemon_image, current_opponent_image, current_pokemon_label,
                           current_opponent_label]:
                if widget is not None:
                    widget.destroy()

            # Create Pokemon and Opponent labels

            current_pokemon_image = tk.Label(battle_frame, image=current.get_sprite("back"))
            current_pokemon_image.place(relx=0.05, rely=0.9175, anchor=tk.SW)

            current_pokemon_label = tk.Label(battle_frame, text=f"{current.nickname}\tLv. {current.level}", width=20,
                                             anchor=tk.W)
            current_pokemon_label.place(relx=0.035, rely=1, anchor=tk.SW)

            current_opponent_image = tk.Label(battle_frame, image=opponent.get_sprite("front"))
            current_opponent_image.place(relx=0.95, rely=0.135, anchor=tk.NE)

            current_opponent_label = tk.Label(battle_frame, text=f"{opponent.nickname}\tLv. {opponent.level}", width=20,
                                              anchor=tk.E)
            current_opponent_label.place(relx=0.975, rely=0.025, anchor=tk.NE)

            # Iterate each label
            for pkm, label in [(current, current_pokemon_label), (opponent, current_opponent_label)]:
                # Check if Pokemon is shiny
                if pkm.shiny:
                    # Update text in label
                    label.config(text="✨ " + label.cget("text"))

        # Define a catch start event callback
        def on_catch_start(ball: Ball):
            print("start")
            # Declare nonlocal variables
            nonlocal current_opponent_image, poke_ball_image, poke_ball_original_x

            if current_opponent_image is None:
                print("Received catch start event before an opponent image was drawn")
                return  # Should never happen, exit

            # Create a label for the poke ball and destroy the current opponent image
            poke_ball_image = tk.Label(battle_frame, image=images.get_image(f"item_{ball.name.lower()}"))
            poke_ball_image.place(x=340, y=50, anchor=tk.NE)

            # Store the original position immediately after placement
            poke_ball_original_x = 350

            # Destroy opponent image
            current_opponent_image.destroy()
            current_opponent_image = None

        # Define a catch shake event callback
        def on_catch_shake():
            print("shake")
            # Declare nonlocal variables
            nonlocal poke_ball_image, poke_ball_original_x

            # Define the shake animation with proper scheduling
            def _shake(count=0, direction=2):
                # Move the ball in the current direction
                poke_ball_image.place(x=poke_ball_original_x + direction, y=poke_ball_image.winfo_y())

                count += 1
                # If we've completed the animation, reset to original position
                if count >= 6:  # 3 full shakes
                    poke_ball_image.place(x=poke_ball_original_x, y=poke_ball_image.winfo_y())
                    return

                # Schedule the next frame with reversed direction
                self.window.after(50, lambda: _shake(count, -direction))

            # Start the shake animation
            _shake()

        # Define a catch fail event callback
        def on_catch_fail():
            print("fail")
            # Declare nonlocal variables
            nonlocal current_opponent_image, poke_ball_image, last_catch_attempt

            # First destroy the poke ball image
            if poke_ball_image is not None:
                poke_ball_image.destroy()
                poke_ball_image = None

            # Then recreate the opponent image
            current_opponent_image = tk.Label(battle_frame, image=self.battle.current_opponent.get_sprite("front"))
            current_opponent_image.place(relx=0.95, rely=0.135, anchor=tk.NE)

            # Update last_catch_attempt
            last_catch_attempt = time.time()

        # Define a catch success event callback
        def on_catch_success():
            print("success")

        # Attach listener callbacks
        self.battle.on(BattleEvent.CURRENT_POKEMON_UPDATE, on_current_pokemon_update)

        # Create a container frame to center the action frame
        container_frame = tk.Frame(self.window)
        container_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # Create an action frame inside the container
        action_frame = tk.Frame(container_frame)
        action_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        # Initialize a key-callback map
        keyed_callbacks = {}

        # Define the key listener callback
        def on_key(event):
            # Check if there is a matching callback
            if event.keysym in keyed_callbacks:
                # Call the callback
                keyed_callbacks[event.keysym]()

        # Bind on_key listener
        self.window.bind('<Key>', on_key)

        # Create a helper function to make pretty buttons
        def create_button(text: str, row: int, col: int, bg: str, active_bg: str, key: str, callback: Callable[[], None]):
            # Create the button
            button = tk.Button(
                action_frame,
                text=f"{text} [{key.upper()}]",
                relief=tk.GROOVE,
                bd=3,
                padx=50,
                pady=8,
                width=10,
                bg=bg,
                activebackground=active_bg,
                font=get_bold_font(),
                command=callback
            )
            # Pack the button
            button.grid(row=row, column=col, padx=5, pady=5)
            # Put key and callback in keyed-callback map
            keyed_callbacks[key] = callback

        # Create a fight callback
        def fight():
            MoveSelector(self.parent, self.battle.current, lambda a: print(a)).draw().wait()

        # Create a catch callback
        def catch():
            nonlocal last_catch_attempt

            # Ensure last catch attempt was more than a second ago
            if not time.time() > last_catch_attempt + 1:
                return # Exit

            # Check if the poke ball image exists as a cooldown measure
            if poke_ball_image is not None:
                return # Exit

            # Check if the player has any items in their bag
            if len(holder.save.bag.items()) == 0:
                # Show a dialogue message saying that their bag is empty
                messagebox.showerror("Empty Bag!", "You don't have any items in your bag")
                return # Exit

            # Define a callback handler for the item selector
            def on_select(item: str):
                # Get ball object from item
                ball = Ball.of(item)
                # Consume the item
                holder.save.consume_item(item)
                # Call the catch method
                self.battle.catch(ball)

            # Create an item selector instance
            ItemSelector(self.parent, on_select).draw().wait()

        # Create a Pokemon callback
        def pokemon():
            pass

        # Create a run callback
        def run():
            pass

        # Create the buttons
        create_button("FIGHT", 0, 0, "#f96d5f", "#b44d43", "z", fight)
        create_button("CATCH", 0, 1, "#ffd233", "#c9a72c", "x", catch)
        create_button("POKEMON", 1, 0, "#61d18a", "#3c8757", "c", pokemon)
        create_button("RUN", 1, 1, "#5f7ff9", "#354a97", "v", run)

        # Configure grid to center the contents
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        # Return an instance of self
        return self