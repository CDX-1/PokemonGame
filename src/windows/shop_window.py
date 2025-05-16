# This file defines the shop where users can purchase items
# and heal their Pokemon

# Imports

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from src import holder
from src.pokemon.types.ball import Ball
from src.utils.font import get_bold_font
from src.windows.abstract.top_level_window import TopLevelWindow

# Define the 'ShopWindow' class
class ShopWindow(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, and a rerender callback
    def __init__(self, parent: tk.Wm | tk.Misc, rerender: Callable[[], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.rerender = rerender

    # Define a function to nicely format numbers in a currency format
    def format(self, num: int):
        return f"{num:,}"

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Shop", width=400, height=350)

        # Create a header label
        header = tk.Label(self.window, text="Shop", font=get_bold_font())
        header.pack(pady=(10, 0))

        # Create a balance label
        balance = tk.Label(self.window, text=f"Balance: ¥{self.format(holder.save.yen)}")
        balance.pack()

        # Define a callback to update the balance
        def update_balance():
            balance.config(text=f"Balance: ¥{self.format(holder.save.yen)}")

        # Create a frame for the shop buttons
        shop_frame = tk.Frame(self.window)
        shop_frame.pack()

        # Iterate every ball type and their price
        for ball, price, color in [
            (Ball.POKE_BALL, 200, "#CC0000"),
            (Ball.GREAT_BALL, 600, "#2A5DAA"),
            (Ball.ULTRA_BALL, 1200, "#424242"),
            (Ball.QUICK_BALL, 1000, "#FFF200"),
            (Ball.MASTER_BALL, 99999, "#5D3AA8")
        ]:
            # Define a buy callback
            def buy(b_ball: Ball, b_price: int):
                # Create a temporarily top level window for the user to enter a number
                buy_window = TopLevelWindow.create_basic_window("Enter an amount", width=200, height=100)
                # Create a header label
                header = tk.Label(buy_window, text="Enter an amount", font=get_bold_font())
                header.pack()
                # Create a variable to store the amount
                amount_var = tk.StringVar()
                # Create an entry widget to modify the amount variable
                entry = tk.Entry(buy_window, textvariable=amount_var, width=10)
                entry.pack()
                # Define a confirmation callback
                def confirm():
                    # Destroy the top level window
                    buy_window.destroy()
                    # Verify the value of the amount variable
                    try:
                        # Try casting amount variable to an int
                        amount = int(amount_var.get())
                    except ValueError:
                        # Show an error if casting failed
                        messagebox.showerror("Invalid Amount", "You enter an invalid amount to buy")
                        return # Exit
                    # Check if the player can afford amount of item
                    total_cost = amount * b_price
                    if holder.save.yen - total_cost < 0:
                        messagebox.showerror("Not Enough Yen", "You are " +\
                                             f"¥{self.format(total_cost - holder.save.yen)} short!")
                        return # Exit
                    # Deduct yen
                    holder.save.yen -= total_cost
                    # Add item to the player's bag
                    ball_name = b_ball.name.replace("_", " ").title()
                    # Check if the player already has at least one of this item
                    if ball_name in holder.save.bag:
                        # Increase the amount directly
                        holder.save.bag[b_ball.name.lower()] += amount
                    else:
                        # Create the key-value pair
                        holder.save.bag[b_ball.name.lower()] = amount
                    # Show message
                    messagebox.showinfo("Receipt", "Successfully bought " +\
                                        f"{ball_name} for ¥{self.format(total_cost)}!")
                    # Call the update callback
                    update_balance()
                # Create a button to confirm the amount
                confirm = tk.Button(buy_window, text="Confirm", command=confirm, width=10)
                confirm.pack()
                # Show the window
                buy_window.transient(self.parent)

            ball_name = ball.name.replace("_", " ").title()
            # Create a button for the item
            button = tk.Button(shop_frame, text=f"{ball_name} - ¥{self.format(price)}", width=20, padx=10, pady=5, bd=3,
                               command=lambda b=ball, p=price: buy(b, p), bg=color)
            button.pack()

        # Define a callback to heal the player's team
        def heal_team():
            # Iterate the player's team
            for pokemon in holder.save.team:
                # Return to max health
                pokemon.condition.health = pokemon.get_max_health()
                # Restore PP of moves
                for move in pokemon.condition.move_set:
                    move.pp = move.max_pp

            # Show a messagebox
            messagebox.showinfo("Healed Team", "Your team has been healed.")

            # Call the rerender callback
            self.rerender()

        # Add a button to heal the player's team
        heal_button = tk.Button(shop_frame, text="Heal Pokemon", width=20, padx=10, pady=5, bd=3, command=heal_team)
        heal_button.pack()

        # Add a button to cancel
        close_button = tk.Button(shop_frame, text="Close", width=20, padx=10, pady=5, bd=3,
                                  command=self.window.destroy)
        close_button.pack()

        # Return an instance of self
        return self