# This file contains a top level window that allows a player to choose an item
# from their bag

# Imports

import tkinter as tk
from typing import Callable

from src import holder
from src.utils import images
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# Define the 'ItemSelector' class
class ItemSelector(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root, and a ready callback
    def __init__(self, parent: tk.Wm | tk.Misc, callback: Callable[[str], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)

        # Initialize fields
        self.callback = callback

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window(f"Select an Item", width=400, height=300)

        # Create a container frame
        frame = tk.Frame(self.window)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Create a title
        title_label = tk.Label(frame, text="Select an item:")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Create a variable to store the selected item
        selected_item = tk.IntVar()

        # Initialize an item map
        items = {}

        # Iterate all items in player's bag, enumerated
        for i, pair in enumerate(holder.save.bag.items()):
            # Spread the pair
            item, amount = pair
            # Create a frame for the item
            item_frame = tk.Frame(frame)
            item_frame.grid(row=i + 1, column=0, columnspan=2)
            # Create a radio button
            item_radio = tk.Radiobutton(item_frame, text=f"{' '.join(item.split('_')).title()} x{amount}", value=i, variable=selected_item)
            item_radio.grid(row=0, column=0)
            # Create an image label
            image_label = tk.Label(item_frame, image=images.get_image(f"item_{item.lower()}"))
            image_label.grid(row=0, column=1)
            # Put item in map
            items[i] = item

        # Create a button frame
        button_frame = tk.Frame(frame)
        button_frame.grid(row=len(holder.save.bag.items()) + 2, column=0, columnspan=2, pady=(10, 0))

        # Define the select callback
        def on_select():
            # Check if there is any selection
            if selected_item.get() is None:
                # Destroy window and exit
                self.window.destroy()
                return

            # Call the callback function using the selected item
            self.callback(items[selected_item.get()])
            # Destroy the window
            self.window.destroy()

        # Add a select button
        select_button = tk.Button(button_frame, text="SELECT", font=get_bold_font(), width=5, padx=3, pady=3,
                                  relief=tk.GROOVE, command=on_select)
        select_button.grid(row=0, column=0)

        # Add a cancel button
        cancel_button = tk.Button(button_frame, text="CANCEL", font=get_bold_font(), width=5, padx=3, pady=3,
                                  relief=tk.GROOVE, command=lambda: self.window.destroy())
        cancel_button.grid(row=0, column=1)

        # Return an instance of self
        return self