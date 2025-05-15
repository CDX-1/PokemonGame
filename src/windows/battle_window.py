# This file defines a window that serves as the visual representation
# of a Pokemon battle
import math
# Imports

import tkinter as tk
from tkinter import messagebox
from typing import Callable
import time

from src import holder
from src.game.battle_client import BattleClient, BattleEvent, Battler
from src.pokemon.pokemon import Pokemon
from src.pokemon.types.ball import Ball
from src.pokemon.types.capture_data import CaptureData
from src.pokemon.types.stat import Stat
from src.utils import images
from src.utils.font import get_bold_font, get_mono_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow
from src.windows.item_selector import ItemSelector
from src.windows.move_selector import MoveSelector
from src.windows.nicknamer import Nicknamer
from src.windows.pokemon_selector import PokemonSelector

# Define the 'BattleWindow' class
class BattleWindow(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, a Battle object, and a rerender callback
    def __init__(self, parent: tk.Wm | tk.Misc, battle: BattleClient, rerender: Callable[[], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.battle = battle
        self.rerender = rerender
        self.buttons = []
        self.child_windows = []

        # Initialize widgets that need class-level scope
        self.current_pokemon_image = None
        self.current_opponent_image = None
        self.current_pokemon_label = None
        self.current_opponent_label = None
        self.current_pokemon_health_frame = None
        self.current_pokemon_health_bar = None
        self.current_opponent_health_frame = None
        self.current_opponent_health_bar = None
        self.poke_ball_image = None
        self.poke_ball_original_x = 0
        self.last_catch_attempt = 0
        self.log_label = None
        self.is_logging = False
        self.log_queue = []
        self.keyed_callbacks = {}

    # Create a function to lock the buttons
    def lock(self):
        # Iterate each button
        for button_data in self.buttons:
            # Spread the button data
            button, callback = button_data
            # Override the command
            button.configure(command=lambda: print("Locked"))

        # Iterate each child window
        for window in self.child_windows:
            # Ensure window has not already been destroyed
            if window is not None:
                # Destroy the window
                window.destroy()

        # Empty the list
        self.child_windows.clear()

    # Create a function to unlock the buttons
    def unlock(self):
        # Iterate each button with their callbacks
        for button_data in self.buttons:
            # Spread tuple
            button, callback = button_data
            # Override the command
            button.configure(command=callback)

    # Helper function to create and update a health bar
    def create_health_bar(self, parent_frame, x, y, anchor, pkm: Pokemon):
        # Create health bar frame
        health_frame = tk.Frame(parent_frame, bd=1, relief=tk.SUNKEN)
        health_frame.place(relx=x, rely=y, anchor=anchor, width=150, height=15)

        # Create health bar canvas
        health_bar = tk.Canvas(health_frame, bg="white", highlightthickness=0)
        health_bar.pack(fill=tk.BOTH, expand=True)

        # Update the health bar (initial render)
        self.update_health_bar(health_bar, pkm.condition.health, pkm.get_stat(Stat.HP))

        return health_frame, health_bar

    # Helper function to update the health bar
    def update_health_bar(self, health_bar, current_hp, max_hp):
        if health_bar is None:
            return

        # Calculate health percentage
        health_percentage = current_hp / max_hp

        # Choose color based on health percentage
        health_color = "#00CC00" if health_percentage > 0.5 else "#FFCC00" if health_percentage > 0.2 else "#FF0000"

        # Clear and redraw the health bar
        health_bar.delete("all")
        health_bar.create_rectangle(0, 0, 150 * health_percentage, 15, fill=health_color, outline="")

    # Define the key listener callback
    def on_key(self, event):
        # Check if there is a matching callback
        if event.keysym in self.keyed_callbacks:
            # Call the callback
            self.keyed_callbacks[event.keysym]()

    # Create a helper function to make pretty buttons
    def create_button(self, text: str, row: int, col: int, bg: str, active_bg: str, key: str,
                      callback: Callable[[], None], action_frame):
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
        self.keyed_callbacks[key] = callback
        # Return the button
        return button

    # Create a fight callback
    def fight(self):
        # Define a move selection callback
        def on_select(move):
            # Lock buttons
            self.lock()
            # Select the move
            self.battle.select_move(Battler.PLAYER, move)

        # Create window
        window = MoveSelector(self.parent, self.battle.current, on_select)
        # Append to children
        self.child_windows.append(window.window)
        # Show window
        window.draw().wait()

    # Create a catch callback
    def catch(self):
        # Ensure last catch attempt was more than a second ago
        if not time.time() > self.last_catch_attempt + 1:
            return  # Exit

        # Check if the poke ball image exists as a cooldown measure
        if self.poke_ball_image is not None:
            return  # Exit

        # Check if the player has any items in their bag
        if len(holder.save.bag.items()) == 0:
            # Show a dialogue message saying that their bag is empty
            messagebox.showerror("Empty Bag!", "You don't have any items in your bag")
            return  # Exit

        # Define a callback handler for the item selector
        def on_select(item: str):
            # Get ball object from item
            ball = Ball.of(item)
            # Consume the item
            holder.save.consume_item(item)
            # Call the catch method
            self.battle.catch(ball)

        # Create an item selector instance
        window = ItemSelector(self.parent, on_select)
        # Append the window
        self.child_windows.append(window.window)
        # Show window
        window.draw().wait()

    # Create a Pokemon callback
    def pokemon(self):
        # Define the Pokemon selection callback
        def on_select(pokemon: Pokemon):
            # Call the switch function
            self.battle.switch(Battler.PLAYER, pokemon)

        # Create window
        window = PokemonSelector(self.parent, self.battle.current, on_select, True)
        # Append to children
        self.child_windows.append(window.window)
        # Show window
        window.draw().wait()

    # Create a run callback
    def run(self):
        pass

    # Define a function that will show a message on the battle menu
    def log(self, message: str, expire: int = 1000):
        # Add the message to the queue
        self.log_queue.append((message, expire))

        # Check if we're currently logging
        if self.is_logging:
            return  # Exit

        # Process the next message from the queue
        self.process_next_message()

    # Define a function to process the next message in the queue
    def process_next_message(self):
        # Check if there is another message
        if self.log_queue:
            # Pop the next message from the queue
            current_message, current_expire = self.log_queue.pop(0)
            self.is_logging = True

            # Check if current message is None
            if current_message is None:
                # Schedule the next message because this is an intentional blockage
                self.window.after(current_expire, self.on_log_expire)
            else:
                # Place the label on screen before starting animation
                self.log_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.log_label.config(text="")  # Clear previous text

                # Iterate each character in the message, enumerated
                for i, char in enumerate(current_message):
                    self.window.after(i * 10, lambda j=i: self.log_label.config(text=current_message[:j + 1]))

                # Schedule the expiry
                self.window.after(len(current_message) * 10 + current_expire, self.on_log_expire)

    # Define the expiry callback for log messages
    def on_log_expire(self):
        # Unplace the label
        self.log_label.place_forget()
        # Switch is_logging to False
        self.is_logging = False

        # After the message expires, process the next message
        self.window.after(0, self.process_next_message)

    def block_logs(self, duration: int):
        # Insert an empty message to temporarily block the log
        self.log(None, duration)

    # Define a function to destroy the battle
    def destroy(self):
        self.rerender() # Call the rerender callback
        self.window.destroy() # Destroy the window
        holder.battle = None # Set the current battle to none
        self.battle.disconnect() # Disconnect from the TCP socket

    # Define the ready callback
    def on_start(self):
        self.battle.start()
        self.battle.send_teams()
        self.battle.send_layouts()

    # Define a turn change callback
    def on_turn_change(self, turn):
        # Ensure buttons are unlocked
        self.unlock()

    # Define a health update callback
    def on_health_update(self, battler: Battler, health: int):
        # Check which battler's health is being updated
        if battler == Battler.PLAYER:
            # Update player Pokemon's health bar
            self.update_health_bar(self.current_pokemon_health_bar, health, self.battle.current.get_max_health())
        elif battler == Battler.AI:
            # Update opponent Pokemon's health bar
            self.update_health_bar(self.current_opponent_health_bar, health,
                                   self.battle.current_opponent.get_max_health())

    # Define current pokemon update event callback
    def on_current_pokemon_update(self, current: Pokemon, opponent: Pokemon):
        # Destroy Pokemon label or Opponent label if existing
        for widget in [self.current_pokemon_image, self.current_opponent_image, self.current_pokemon_label,
                       self.current_opponent_label, self.current_pokemon_health_frame,
                       self.current_opponent_health_frame]:
            if widget is not None:
                widget.destroy()

        # Create Pokemon and Opponent labels
        self.current_pokemon_image = tk.Label(self.battle_frame, image=current.get_sprite("back"))
        self.current_pokemon_image.place(relx=0.05, rely=0.93, anchor=tk.SW)

        self.current_pokemon_label = tk.Label(self.battle_frame, text=f"{current.nickname}\tLv. {current.level}",
                                              width=20, anchor=tk.W)
        self.current_pokemon_label.place(relx=0.035, rely=0.935, anchor=tk.SW)

        # Create player's Pokemon health bar
        self.current_pokemon_health_frame, self.current_pokemon_health_bar = self.create_health_bar(
            self.battle_frame, 0.035, 1, tk.SW, current
        )

        self.current_opponent_image = tk.Label(self.battle_frame, image=opponent.get_sprite("front"))
        self.current_opponent_image.place(relx=0.95, rely=0.21, anchor=tk.NE)

        self.current_opponent_label = tk.Label(self.battle_frame, text=f"{opponent.nickname}\tLv. {opponent.level}",
                                               width=20, anchor=tk.E)
        self.current_opponent_label.place(relx=0.975, rely=0.025, anchor=tk.NE)

        # Create opponent's Pokemon health bar
        self.current_opponent_health_frame, self.current_opponent_health_bar = self.create_health_bar(
            self.battle_frame, 0.975, 0.13, tk.NE, opponent
        )

        # Iterate each label
        for pkm, label in [(current, self.current_pokemon_label), (opponent, self.current_opponent_label)]:
            # Check if Pokemon is shiny
            if pkm.shiny:
                # Update text in label
                label.config(text="✨ " + label.cget("text"))

    # Define a utility function to replace the opponent image with a Pokeball
    def start_catch_effect(self, ball: Ball):
        # Lock actions
        self.lock()

        if self.current_opponent_image is None:
            print("Received catch start event before an opponent image was drawn")
            return  # Should never happen, exit

        # Create a label for the poke ball and destroy the current opponent image
        self.poke_ball_image = tk.Label(self.battle_frame, image=images.get_image(f"item_{ball.name.lower()}"))
        self.poke_ball_image.place(x=340, y=50, anchor=tk.NE)

        # Store the original position immediately after placement
        self.poke_ball_original_x = 350

        # Destroy opponent image
        self.current_opponent_image.destroy()
        self.current_opponent_image = None

    # Define utility function to make the Pokeball image shake
    def shake_pokeball(self, count=0, direction=2):
        # Move the ball in the current direction
        self.poke_ball_image.place(x=self.poke_ball_original_x + direction, y=self.poke_ball_image.winfo_y())

        count += 1
        # If we've completed the animation, reset to original position
        if count >= 6:  # 3 full shakes
            self.poke_ball_image.place(x=self.poke_ball_original_x, y=self.poke_ball_image.winfo_y())
            return

        # Schedule the next frame with reversed direction
        self.window.after(50, lambda: self.shake_pokeball(count, -direction))

    # Define a catch event callback
    def on_catch(self, is_success: bool, ball: Ball, shakes: int):
        # Log the event
        self.log(f"Threw a {' '.join(ball.name.split('_')).lower().title()}")
        # Call the start catch effect function
        self.start_catch_effect(ball)
        # Shake 'shake' many times
        for i in range(shakes):
            self.window.after(i * 1000 + 500, self.shake_pokeball)

        # Schedule after-shakes callback
        self.window.after(shakes * 1000 + 1000, lambda: self.after_catch(ball, is_success))

        # Temporarily block logs
        self.block_logs(shakes * 1000)

        # Add success/failure message
        if is_success:
            self.log(f"{self.battle.current_opponent.nickname} was caught!")
        else:
            self.log(f"{self.battle.current_opponent.nickname} broke free!")

    # Define a function to be called after the catch animation
    def after_catch(self, ball: Ball, is_success: bool):
        # Check if catch is successful
        if is_success:
            # Set the Pokemon's capture data
            capture_data = CaptureData(
                ball,
                holder.save.name,
                holder.save.trainer_id
            )
            self.battle.current_opponent.capture_data = capture_data
            # Prompt the player to set the Pokemon's nickname
            Nicknamer(self.window, self.battle.current_opponent).draw().wait()
            # Check if the player's team is full (six members)
            if len(holder.save.team) >= 6:
                # Initialize a sentinel value
                has_found_box = False
                # Find the first box that has less than 30 Pokemon
                for box in holder.save.box:
                    # Check if the length of this box exceeds or is 30
                    if len(box) >= 30:
                        continue # Keep searching
                    else:
                        # Add the Pokemon to that box
                        box.append(self.battle.current_opponent)
                        has_found_box = True
                        break
                # Check if we have found a box
                if not has_found_box:
                    # Append a box to the box list
                    holder.save.box.append([])
                    # Append this Pokemon to the last box
                    holder.save.box[-1].append(self.battle.current_opponent)

                # Log event
                self.log(f"{self.battle.current_opponent.nickname} has been sent to the box!")
            else:
                # Add the Pokemon to the player's party
                holder.save.team.append(self.battle.current_opponent)
                # Log event
                self.log(f"{self.battle.current_opponent.nickname} has been added to your party!")

            # After 1.5 seconds, destroy the window
            self.window.after(1500, self.destroy)
        else:
            # First destroy the poke ball image
            if self.poke_ball_image is not None:
                self.poke_ball_image.destroy()
                self.poke_ball_image = None

            # Then recreate the opponent image
            self.current_opponent_image = tk.Label(self.battle_frame,
                                                   image=self.battle.current_opponent.get_sprite("front"))
            self.current_opponent_image.place(relx=0.95, rely=0.21, anchor=tk.NE)

            # Unlock actions
            self.unlock()

    # Define a PP update event callback
    def on_pp_update(self, pokemon: Pokemon, pp_data: dict[str, int]):
        # Iterate each move and their PP count
        for move, pp in pp_data.items():
            # Get the battle move object by filtering the move set
            battle_move = list(filter(lambda entry: entry.name == move, pokemon.condition.move_set))[0]
            battle_move.pp = pp

    # Define a stat change event callback
    def on_stat_change(self, pokemon: Pokemon, stat: str, amount: int):
        # Initialize the keyword
        keyword = "increased"

        # Check if the stat has increased or decreased
        if amount < 0:
            keyword = "decreased"

        # Log the event
        self.log(f"{pokemon.nickname}'s {stat} has {keyword} by {amount} stages")

    # Define a critical hit event callback
    def on_critical_hit(self, pokemon: Pokemon):
        # Log the event
        self.log("A critical hit!")

    # Define a super effective move event callback
    def on_super_effective(self, pokemon: Pokemon):
        # Log the event
        self.log(f"It's super effective!")

    # Define a critical hit event callback
    def on_resisted(self, pokemon: Pokemon):
        # Log the event
        self.log(f"It's not very effective...")

    # Define a super effective move event callback
    def on_immune(self, pokemon: Pokemon):
        # Log the event
        self.log(f"It doesn't affect {pokemon.nickname}...")

    # Define a faint event callback
    def on_faint(self, pokemon: Pokemon):
        # Log events
        self.log(f"{pokemon.nickname} has fainted!")

        # Check if the fainted Pokemon belongs to the player
        if not pokemon in self.battle.player:
            # Update opponent health bar
            self.update_health_bar(self.current_opponent_health_bar, 0, self.battle.current_opponent.get_max_health())
            return # Exit
        else:
            # Update player health bar
            self.update_health_bar(self.current_pokemon_health_bar, 0, self.battle.current.get_max_health())

        # Check if the player has any healthy Pokemon remaining
        if len(list(filter(lambda entry: entry.get_health() > 0, self.battle.player))) == 0:
            return # Exit

        # Define an on select callback
        def on_select(selection: Pokemon):
            # Call the switch function
            self.battle.switch(Battler.PLAYER, selection)

        # Define the after callback
        def after():
            # Prompt the player to select their next Pokemon
            PokemonSelector(self.window, self.battle.current, on_select, False).draw().wait()

        # Schedule the after function 1 second later
        self.window.after(1000, after)

    # Define the end event callback
    def on_end(self, won: bool):
        # Check if we won
        if won:
            # Define variables
            b = self.battle.current_opponent.get_species().base_exp
            l = self.battle.current_opponent.level
            a = 1.5 if self.battle.is_trainer else 1
            t = 1.5 if self.battle.current.capture_data.original_trainer_id != holder.save.trainer_id else 1
            e = 1
            s = 1
            # Calculate the amount of experience to reward
            exp = math.floor(((a * b * l) / 5) * t * e * (1 / s))
            # Add exp to the Pokemon
            has_leveled_up = self.battle.current.add_exp(exp)
            # Calculate the amount of yen to reward
            yen = int(10000 * ((b * l ** 1.3) / (608 * 100 ** 1.3)) ** 0.8)
            # Add the yen
            holder.save.yen += yen
            # Log events
            self.log(f"{self.battle.current.nickname} has gained {exp} EXP!")
            if has_leveled_up:
                self.log(f"{self.battle.current.nickname} has leveled up to level {self.battle.current.level}!")
            self.log(f"You have defeated {self.battle.current_opponent.nickname}, you have received ¥{yen}")
        else:
            # Define variables
            b = self.battle.current_opponent.get_species().base_exp
            l = self.battle.current_opponent.level
            # Calculate the amount of yen to reward
            yen = int(1000 * ((b * l ** 1.2) / (608 * 100 ** 1.2)) ** 0.8)
            # Deduct the yen with a specified minimum
            holder.save.yen = max(holder.save.yen - yen, 0)
            # Log event
            self.log(f"You have been defeated! You dropped ¥{yen} whilst panicking!")

        # Destroy the window after a delay
        self.window.after(5000, self.destroy)

    # Define a move event callback
    def on_move(self, user: Pokemon, move: str, target: Pokemon, miss: bool, still: bool):
        # Log events
        self.log(f"{user.nickname} used {move} on {target.nickname}")
        if miss:
            self.log(f"{self.battle.current_opponent.nickname} missed!")

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Battle", width=400, height=300)

        # Set the delete handler
        self.window.protocol("WM_DELETE_WINDOW", self.destroy)

        # Create a battle frame
        self.battle_frame = tk.Frame(self.window)
        self.battle_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Create a container frame to center the action frame
        container_frame = tk.Frame(self.window)
        container_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # Create an action frame inside the container
        action_frame = tk.Frame(container_frame)
        action_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        # Bind on_key listener
        self.window.bind('<Key>', self.on_key)

        # Create the buttons
        fight_button = self.create_button("FIGHT", 0, 0, "#f96d5f", "#b44d43", "z", self.fight, action_frame)
        catch_button = self.create_button("CATCH", 0, 1, "#ffd233", "#c9a72c", "x", self.catch, action_frame)
        pokemon_button = self.create_button("POKEMON", 1, 0, "#61d18a", "#3c8757", "c", self.pokemon, action_frame)
        run_button = self.create_button("RUN", 1, 1, "#5f7ff9", "#354a97", "v", self.run, action_frame)

        # Store buttons and callbacks
        self.buttons = [
            (fight_button, self.fight),
            (catch_button, self.catch),
            (pokemon_button, self.pokemon),
            (run_button, self.run)
        ]

        # Configure grid to center the contents
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_columnconfigure(1, weight=1)

        # Create a label that will overlay the battle action frame to show messages
        self.log_label = tk.Label(action_frame, text="", font=get_mono_font(12), wraplength=380,
                                  anchor=tk.NW, justify=tk.LEFT, bg="#f0f0f0")

        # Attach listener callbacks
        self.battle.on(BattleEvent.STARTED, self.on_start)
        self.battle.on(BattleEvent.HEALTH_UPDATE, self.on_health_update)
        self.battle.on(BattleEvent.CURRENT_POKEMON_UPDATE, self.on_current_pokemon_update)
        self.battle.on(BattleEvent.CATCH, self.on_catch)
        self.battle.on(BattleEvent.MOVE, self.on_move)
        self.battle.on(BattleEvent.TURN_CHANGE, self.on_turn_change)
        self.battle.on(BattleEvent.PP_UPDATE, self.on_pp_update)
        self.battle.on(BattleEvent.STAT_CHANGE, self.on_stat_change)
        self.battle.on(BattleEvent.CRITICAL_HIT, self.on_critical_hit)
        self.battle.on(BattleEvent.SUPER_EFFECTIVE, self.on_super_effective)
        self.battle.on(BattleEvent.RESISTED, self.on_resisted)
        self.battle.on(BattleEvent.IMMUNE, self.on_immune)
        self.battle.on(BattleEvent.FAINTED, self.on_faint)
        self.battle.on(BattleEvent.END, self.on_end)

        # Create the battle
        self.battle.create()
        self.battle.window = self

        # Return an instance of self
        return self