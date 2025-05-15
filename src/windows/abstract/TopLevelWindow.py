# This file contains an abstract super class called TopLevelWindow which
# will be inherited by every class definition for a top level window. This
# super class makes it easier to write the code for a top level window and
# provides helpful methods such as wait().

# Imports

# This is used to allow the 'TopLevelWindow' class to return itself in its methods/functions
from __future__ import annotations

import tkinter as tk

from src.utils import images


# Define the 'TopLevelWindow' class
class TopLevelWindow:
    # Class constructor method takes a 'parent' element such as the Tkinter root
    def __init__(self, parent: tk.Wm | tk.Misc):
        # Initialize fields
        self.parent = parent
        # A blank variable that will contain an instance of our top level window
        self.window: tk.Toplevel | None = None

    # This is a method that is intended to be overridden by inheriting subclasses
    # to draw Tkinter elements onto the TopLevel window
    def draw(self) -> TopLevelWindow:
        return self

    # Define the 'wait' method that locks the user into this
    # top level window and blocks Tkinter until this window has
    # been destroyed. 'factory' API architecture can be used
    # (method-chaining)
    def wait(self) -> TopLevelWindow:
        # Force this window to be on top of parent window
        self.window.transient(self.parent)
        # Force the window to be focused
        self.window.focus_force()
        # Starts a local loop and does not exist until this
        # window is destroyed
        self.window.wait_window()
        # Return an instance of self
        return self

    # This static method creates a basic top level window that specifies
    # parameters such as title and size, and then it returns that window.
    @staticmethod
    def create_basic_window(title: str, width: int, height: int) -> tk.Toplevel:
        # Create the top level window
        window = tk.Toplevel()
        # Set the window title
        window.title(title)
        # Set the window size
        window.geometry(f"{width}x{height}")
        # Make the window not resizable
        window.resizable(False, False)
        # Return the window
        return window

    # This static method creates a containerizing frame that lays out all
    # Tkinter elements horizontally centered.
    @staticmethod
    def create_basic_frame(parent: tk.Misc) -> tk.Frame:
        # Create a container frame
        frame = tk.Frame(parent)
        # Center the frame by filling and expand it with x and y padding
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Return the frame
        return frame

    # This static method creates a label with the logo image and a scale
    @staticmethod
    def create_logo_label(parent: tk.Misc, scale: tuple[int, int] = (8, 8)) -> tk.Label:
        # Create the label using the image 'logo' retrieved from the image utility
        logo_label = tk.Label(parent, image=images.get_image("logo", scale), pady=10)
        logo_label.pack()
        # Return the label
        return logo_label