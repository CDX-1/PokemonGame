# This file contains the definition for the SaveCreator
# top level window which handles the creation of new saves.

# Imports

import json
import random
import time

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from src.game.Save import Save
from src.generator.tools.purifier import purify_obj
from src.pokemon.types.ball import Ball
from src.pokemon.types.capture_data import CaptureData
from src.utils import images
from src.utils.font import get_underline_font, get_font, get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow
import src.holder as holder
from src.windows.nicknamer import Nicknamer

# Create a list that declares the list of starter species
starters = ["bulbasaur", "charmander", "squirtle"]

# The trainer name min length and max length
TRAINER_MIN_LENGTH = 3
TRAINER_MAX_LENGTH = 15

# Define the 'SaveCreator' class
class SaveCreator(TopLevelWindow):
    # Class constructor method takes a 'parent' element such as the Tkinter root and a callback for when a save is created
    def __init__(self, parent: tk.Wm | tk.Misc, callback: Callable[[], None]):
        # Call TopLevelWindow's constructor method
        super().__init__(parent)
        # Initialize fields
        self.callback = callback

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> TopLevelWindow:
        # Create a basic top level window outline
        self.window = TopLevelWindow.create_basic_window("Save Creator", width=400, height=450)
        # Create a container frame
        frame = TopLevelWindow.create_basic_frame(self.window)
        # Create a label that shows the games logo
        TopLevelWindow.create_logo_label(frame)

        # Create a variable to contain the value of the trainer name entry
        name_var = tk.StringVar()

        # Create the prefix label for the trainer name entry
        name_header = tk.Label(frame, text="What's your name, trainer?")
        name_header.pack(fill=tk.X, padx=100)

        # Create the trainer name entry widget
        name_entry = tk.Entry(frame, textvariable=name_var, width=name_header.winfo_width())
        name_entry.pack(fill=tk.X, padx=100)

        # Create the trainer name warning label that specifies the length restriction
        name_warning = tk.Label(frame, text=f"Name must be between {TRAINER_MIN_LENGTH} and " + \
                                            f"{TRAINER_MAX_LENGTH} characters long", fg="red")
        name_warning.pack()

        # Create the starter header label
        starter_header = tk.Label(frame, text="Which one would you like to pick as your starter?\n" + \
                                  "Click the Poke Ball to reveal the Pokemon")
        starter_header.pack()

        # Create a frame to contain the starters
        starters_frame = tk.Frame(frame)
        starters_frame.pack()

        # Retrieve Pokeball image
        pokeball_image = images.get_image("item_poke_ball")

        # Create a Tkinter variable to store which starter was selected
        starter_var = tk.StringVar(value="Selected Starter: ...")
        # Create a raw variable to store the selected starter's actual name
        selected_starter: str | None = None

        # Iterate each starter name, enumerated
        for i, starter in enumerate(starters):
            # Retrieve the species object of the starter
            species = holder.get_species(starter)
            # Create the image label for the starter using the front sprite
            starter_label = tk.Label(starters_frame, image=pokeball_image)
            starter_label.grid(row=0, column=i, pady=5)
            # Create a Tkinter boolean var to store whether the starter's
            # Pokeball has been opened
            opened_var = tk.BooleanVar(value=False)
            # Initialize 'species_label' that will hold the species name
            species_label: tk.Label | None = None
            # Create a callback function to update the label image
            def update_image(species_name: str, opened: tk.BooleanVar, index: int, label: tk.Label, image: tk.PhotoImage):
                # Specify nonlocal 'selected_starter' and 'species_label' variable
                nonlocal selected_starter, species_label
                # Check if the ball has been opened
                if opened.get():
                    # Update the selected starter
                    starter_var.set(f"Selected Starter: {species_name.title()}")
                    selected_starter = species_name
                else:
                    # Update the labels image to the actual Pokemon's sprite
                    label.configure(image=image)
                    # Create a label that shows the species name
                    species_label = tk.Label(starters_frame, text=species_name.title())
                    species_label.grid(row=1, column=index)
                    # Update the opened_var to true
                    opened.set(True)
            # Bind click event to label
            starter_label.bind("<Button-1>", lambda event, species_name=species.name, opened=opened_var, index=i, label=starter_label, image=species.get_sprite("front"): update_image(species_name, opened, index, label, image))

            # Define a callback to handle hover starts
            def on_enter(label: tk.Label | None, event):
                # Check if label is defined
                if label is None:
                    return # Exit callback
                # Apply a highlight thickness to the label to enlarge it
                label.configure(font=get_bold_font())

            # Define a callback to handle hover ends
            def on_leave(label: tk.Label | None, event):
                # Check if label is defined
                if label is None:
                    return  # Exit callback
                # Reset the highlight thickness to 0
                label.configure(font=get_font())

            # Bind the hover start and hover end callbacks
            starter_label.bind("<Enter>", lambda event, label=species_label: on_enter(label, event))
            starter_label.bind("<Leave>", lambda event, label=species_label: on_leave(label, event))

        # Create a label that shows the selected starter
        selected_starter_label = tk.Label(frame, textvariable=starter_var)
        selected_starter_label.pack()

        # Create the 'create' callback function for the create save button
        def create():
            # Check whether the name meets the length restrictions
            name = name_var.get()

            if len(name) < 3 or len(name) > 20:
                # Show error dialogue box
                messagebox.showerror("Invalid Name", f"Your name must be between {TRAINER_MIN_LENGTH} and" + \
                                     f"{TRAINER_MAX_LENGTH} characters long!")
                return # Exit callback

            # Check whether a starter has been selected
            if selected_starter is None:
                # Show error dialogue box
                messagebox.showerror("Invalid Starter", "You must select a starter Pokemon!")
                return # Exit callback

            # Create a random trainer ID between 0 and the 32-bit Integer limit
            trainer_id = random.randint(0, 2147483647)

            # Create an instance of the starter
            starter_pokemon = holder.get_species(selected_starter).spawn(
                levels=7,
                capture_data=CaptureData(
                    ball=Ball.POKE_BALL,
                    original_trainer=name,
                    original_trainer_id=trainer_id
                )
            )

            # Prompt user to select a nickname for their starter
            Nicknamer.prompt_nickname(self.parent, starter_pokemon)

            # Get the current Unix epoch timestamp
            timestamp = int(time.time())

            # Create the save
            save = Save(
                name=name,
                trainer_id=trainer_id,
                created_at=timestamp,
                starter=selected_starter,
                team=[starter_pokemon],
                box=[],
                badges=0,
                yen=300, # Give player 300 yen to start with
                wins=0,
                losses=0
            )

            # Write the save to disk
            # Open the save file in write (W) mode
            with open(f"saves/{trainer_id}-{timestamp}.json", "w") as f:
                # Write purified save object to file
                json.dump(purify_obj(save), f, indent=4)

            # Show dialogue box to inform of completion
            messagebox.showinfo("Save", "Created new save!")
            # Call the callback function
            self.callback()
            # Destroy save creator once complete
            self.window.destroy()

        # Create the button to create the save
        create_button = tk.Button(frame, text="Create", command=create, relief=tk.GROOVE)
        create_button.pack(fill=tk.X, padx=110, pady=10)

        # Create a button to cancel save creation
        cancel_button = tk.Button(frame, text="Cancel", command=lambda: self.window.destroy(), relief=tk.GROOVE)
        cancel_button.pack(fill=tk.X, padx=110)

        # Return an instance of self
        return self