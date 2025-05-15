# This file defines a window that shows the items in the player's bag

# Imports

import tkinter as tk

from src import holder
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define the 'EvolutionWindow' class
class BagWindow(TopLevelWindow):
    # Class constructor method takes a 'parent' element
    def __init__(self, parent: tk.Wm | tk.Misc):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Bag", width=300, height=300)

        # Create a header
        header = tk.Label(self.window, text="Bag", font=get_bold_font())
        header.grid(row=0, column=0, columnspan=2)

        # Create table headers

        item_name_header = tk.Label(self.window, text="Item", font=get_bold_font())
        item_name_header.grid(row=1, column=0)

        item_amt_header = tk.Label(self.window, text="Amount", font=get_bold_font())
        item_amt_header.grid(row=1, column=1)

        # Iterate items in the bag
        for i, data in enumerate(holder.save.bag.items()):
            # Spread the tuple
            item, amount = data
            # Create an item name value label
            item_label = tk.Label(self.window, text=item.replace("_", "".title()))
            item_label.grid(row=i+2, column=0)
            # Create an item amount label
            amount_label = tk.Label(self.window, text=amount)
            amount_label.grid(row=i+2, column=1)

        # Return an instance of self
        return self