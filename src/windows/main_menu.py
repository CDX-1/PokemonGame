# This file contains the code for the main menu which is containerized in
# a Tkinter frame to be embedded in the root window

# Imports

# This is used to allow the 'MainMenu' class to return itself in its methods/functions
from __future__ import annotations

import tkinter as tk
import os
import json
from typing import Callable

from client_tester import test
from src import holder
from src.game.save import Save
from src.windows.abstract.TopLevelWindow import TopLevelWindow
from src.windows.save_creator import SaveCreator

# Define the 'MainMenu' class
class MainMenu:
    # Class constructor method takes a 'parent' element such as the Tkinter root and a
    # callback for once a save has been selected and the main menu is destroyed
    def __init__(self, parent: tk.Wm | tk.Misc, callback: Callable[[], None]):
        # Initialize fields
        self.parent = parent
        self.callback = callback
        # A blank variable that will contain an instance of our frame
        self.frame: tk.Frame | None = None

    # Define the 'draw' method that will create the frame and returns an instance of its
    # self so that the 'factory' API architecture can be used (method-chaining)
    def draw(self) -> MainMenu:
        # Initialize the frame
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Create a container frame
        container = tk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True)

        # TODO Remove
        tk.Button(text="test", command=test).pack()

        # Add the logo
        TopLevelWindow.create_logo_label(container, scale=(15, 15))

        # Create a canvas
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure canvas to work with scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame for all the saves
        saves_frame = tk.Frame(canvas)
        # Create a window in the canvas for the saves
        canvas_frame = canvas.create_window((0, 0), window=saves_frame, anchor=tk.NW)

        # Define a function to update the scroll region when the size of saves_frame updates
        def update_scroll_region(event=None):
            # Ensure the saves_frame is fully updated before calculating bbox
            container.update_idletasks()
            # Update size of scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update width of canvas frame to fit all content
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())

        # Bind the 'update_scroll_region' function to the configure event
        saves_frame.bind("<Configure>", update_scroll_region)

        # Enable mouse wheel scrolling
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind scroll events to the canvas (not bind_all, to limit to canvas)
        canvas.bind("<MouseWheel>", on_mouse_wheel)  # For Windows and macOS trackpads
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Up (macOS/Linux)
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))  # Down (macOS/Linux)

        # Define a function to load all saves
        def load_saves():
            # Iterate all widgets in saves_frame
            for widget in saves_frame.winfo_children():
                # Destroy child widget
                widget.destroy()

            # Initialize a list of saves
            saves = []

            # Create a callback function to load the save
            def callback(loaded_save: Save):
                # Update the holder's current save
                holder.save = loaded_save
                # Destroy main menu
                self.frame.destroy()
                # Call the callback
                self.callback()

            # Iterate all files in /saves/ folder
            for save_file in os.listdir("saves"):
                # Open the save file in read (R) mode with the file referenced as 'f'
                with open(f"saves/{save_file}") as f:
                    # Convert JSON file to Python dictionary
                    data = json.load(f)
                    # Cast dictionary to an instance of 'Save'
                    save = Save.from_obj(data)
                    # Add loaded save to a list of saves
                    saves.append(save)

            # Sort saves list by creation time
            saves = sorted(saves, key=lambda entry: entry.created_at)

            # Iterate all save in saves list
            for save in saves:
                    # Create a frame for the save
                    save_frame = tk.Frame(saves_frame, pady=10)
                    save_frame.pack()

                    # Create a header title for the save name
                    header = tk.Label(save_frame, text=save.name, anchor=tk.W, width=10)
                    header.grid(row=0, column=0)

                    # Create a label showing badges collected
                    badges = tk.Label(save_frame, text=f"Badges: {save.badges}", anchor=tk.W, width=10)
                    badges.grid(row=1, column=0)

                    # Create a frame to show the sprites of the Pokemon in the save's team
                    team_frame = tk.Frame(save_frame)
                    team_frame.grid(row=0, column=1, rowspan=2)

                    # Initialize a counter
                    counter = 1
                    # Iterate all Pokemon in save's team
                    for i, pokemon in enumerate(save.team):
                        # Retrieve Pokemon's sprite
                        sprite = pokemon.get_sprite("front", scale=(2, 2))
                        # Create and pack label for Pokemon's sprite
                        label = tk.Label(team_frame, image=sprite)
                        label.grid(row=0, column=i)
                        counter += 1

                    # Create play button
                    play_button = tk.Button(save_frame, text="Play Save", relief=tk.GROOVE, command = lambda loaded_save=save: callback(loaded_save))
                    play_button.grid(row=2, column=0, columnspan=counter, sticky=tk.EW)

            # Check if 'saves' is empty
            if len(saves) == 0:
                # Create a label that says that no saves exist
                no_saves_label = tk.Label(saves_frame, text="You have no saves")
                no_saves_label.pack()

            # Update size of scroll region
            update_scroll_region()

        # Call 'load_saves'
        load_saves()

        # Define the 'create_new_save' function that will open the
        # save creator top level window
        def create_new_save():
            SaveCreator(self.parent, callback=load_saves).draw().wait()

        # Create a frame to hold the button
        button_frame = tk.Frame(self.frame)
        button_frame.pack()

        # Append a button to create a new save at the bottom of the
        # frame that will call the 'create_new_save' callback
        create_save = tk.Button(button_frame, text="Create New Save", command=create_new_save, relief=tk.GROOVE)
        create_save.pack(pady=5)

        # Return an instance of the MainMenu
        return self