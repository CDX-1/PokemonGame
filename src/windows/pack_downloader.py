# This class contains the top level window for pack downloading
# This window allows the user to pick which packs they want to
# download.

# Imports

# This is used to allow the 'PackDownloader' class to return itself in its methods/functions
from __future__ import annotations

import tkinter as tk

import src.utils.requests as requests
import src.utils.images as images
import src.resources as resources

# Define the 'PackDownloader' class

class PackDownloader:
    # Class constructor method takes a 'parent' element such as the Tkinter root
    def __init__(self, parent: tk.Wm | tk.Misc):
        # Initialize fields
        self.parent = parent
        # A blank variable that will contain an instance of our top level window
        self.window: tk.Toplevel | None = None

    # Define the 'draw' method that returns an instance of its self so that the
    # 'factory' API architecture can be used (method-chaining)
    def draw(self) -> PackDownloader:
        # Initialize the top level window using the parent
        self.window = tk.Toplevel(self.parent)
        # Set the window title
        self.window.title("Pack Downloader")
        # Set the window size
        self.window.geometry("400x400")
        # Make the window not resizable for consistency
        self.window.resizable(False, False)

        # Create a container frame
        frame = tk.Frame(self.window)
        # Center the frame by filling and expand it with x and y padding
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a label that shows the games logo
        logo_label = tk.Label(frame, image=images.get_image("logo", (8, 8)), pady=10)
        logo_label.pack()

        # Create a header label that provides instructions
        header = tk.Label(frame, text="Select the packs you want to download:")
        header.pack()

        # Create a frame that will contain checkboxes
        checkbox_frame = tk.Frame(frame)
        checkbox_frame.pack()

        # Initialize a list of tuples containing a string and a boolean variable
        # This will later be used to ensure that the user has specified at least
        # one pack before continuing.
        checkbutton_list: list[tuple[str, tk.BooleanVar]] = []

        # Iterate the pack resource links with 'i' as the index through the 'enumerate' function
        for i, pack_data in enumerate(resources.packs.items()):
            # Spread the 'pack_data' tuple into an 'identifier' and a 'pack_value'
            identifier, pack_value = pack_data
            # Spread the 'pack_value' into the pack name and the pack's URL
            name, url = pack_value
            # Create a boolean variable to store the state of the checkbox button
            checkbutton_var = tk.BooleanVar()
            # Create a checkbutton in the checkbox frame with the name as the text and bound to the checkbutton variable
            checkbutton = tk.Checkbutton(checkbox_frame, text=name, variable=checkbutton_var, onvalue=True, offvalue=False)
            checkbutton.pack()
            # Add the pack URL and boolean variable to the checkbutton list
            checkbutton_list.append((url, checkbutton_var))

        # Create a frame to contain buttons after the checkbox buttons
        button_frame = tk.Frame(frame, pady=10)
        button_frame.pack()

        # Define the 'proceed' callback function
        def proceed():
            # Iterate all the entries in the checkbutton list
            for data in checkbutton_list:
                # Spread 'data' into the pack URL and the boolean variable
                _pack_url, _var = data

                # If the variable is false then skip
                if not _var.get():
                    continue

                # Print that the pack has started downloading
                print(f"Downloading and unzipping {_pack_url}...")
                # Use the requests utility to download the pack from the URL, unzip it and put it in the packs/ folder
                requests.download(_pack_url, "packs/", True)
                # Print that the pack has finished downloading and unzipping
                print(f"Downloaded and unzipped {_pack_url}")

            # Destroy the top level window
            self.window.destroy()

        # Create a continue button in the button frame that calls the 'proceed' function
        continue_button = tk.Button(button_frame, text="Continue", command=proceed)
        continue_button.pack(pady=5)

        # Create the 'on_checkbutton_var_write' function that will be used to update the
        # 'disabled' state of the continue button so that it is disabled when no checkboxes
        # are selected.
        def on_checkbutton_var_write(*args):
            # Initialize the 'any_true' sentinel variable
            any_true = False

            # Iterate each checkbutton in the checkbutton list
            for _checkbutton in checkbutton_list:
                # Spread the checkbutton into the pack URL and the boolean variable
                _pack_url, _var = _checkbutton
                # Check if the variable is true
                if _var.get():
                    # Set the 'any_true' variable to true
                    any_true = True
                    # Break out of the loop
                    break

            # Check if 'any_true' is true
            if any_true:
                # Set the button to be active
                continue_button.configure(state=tk.ACTIVE)
            else:
                # Otherwise set the button to be disabled
                continue_button.configure(state=tk.DISABLED)

        # Iterate each checkbutton in the checkbutton list
        for checkbutton in checkbutton_list:
            # Spread the checkbutton into the pack URL and the boolean variable
            pack_url, var = checkbutton
            # Attach the 'on_checkbutton_var_write to each boolean variable and
            # listen for the 'write' event
            var.trace_add("write", on_checkbutton_var_write)

        # Call the 'on_checkbutton_var_write' once to set the complete button to disabled
        on_checkbutton_var_write()

        # Return an instance of self
        return self

    # Define the 'wait' method that locks the user into this
    # top level window and blocks Tkinter until this window has
    # been destroyed. 'factory' API architecture can be used
    # (method-chaining)
    def wait(self) -> PackDownloader:
        # Force this window to be on top of parent window
        self.window.transient(self.parent)
        # Disables all other windows
        self.window.grab_set()
        # Starts a local loop and does not exist until this
        # window is destroyed
        self.window.wait_window()
        # Return an instance of self
        return self