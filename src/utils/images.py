# This file provides utility functions for loading and retrieving Tkinter PhotoImages
# and caches them in order to avoid unnecessarily reloading the PhotoImage from disk.

# Imports

import tkinter as tk

# Initialize the caching dictionary which maps a tuple containing a string and a
# sub-tuple containing two integers to a Tkinter PhotoImage. This allows for catching
# of images at different scaling and reusing them without having to rescale the image.

# Example: ("logo", (1, 1)) would be an instance of the logo image
# but ("logo", (2, 2)) would be scaled down and cached so it can be
# reused without the original (1, 1) image having to be rescaled.

cache: dict[tuple[str, tuple[int, int]], tk.PhotoImage] = {}

# Define the 'load_image' function that takes an image name and a file path and returns nothing
def load_image(name: str, path: str):
    # Initialize the Tkinter PhotoImage using the path
    image = tk.PhotoImage(file=path)
    # Store the PhotoImage to the cache with the default (1, 1) size
    cache[(name, (1, 1))] = image

# Define the 'get_image' function that takes an image name and an optional tuple that represents
# how much you want it to be scaled by which defaults to (1, 1) or default scaling and returns a
# Tkinter PhotoImage
def get_image(name: str, scale: tuple[int, int] = (1, 1)) -> tk.PhotoImage:
    # Check if this file is in the cache at this scaling
    if not (name, scale) in cache:
        # Access the image from the cache using the default (1, 1) scaling
        image = cache[(name, (1, 1))]
        # Check if image actually exists
        if image is None:
            # Raise an error to indicate that no image was loaded using this name
            raise KeyError("Image not loaded: " + name)
        # Create a new image that is scaled using subsample
        new_image = image.subsample(*scale)
        # Store this image to the cache using the scaling
        cache[(name, scale)] = new_image
    # Fetch the image from the cache and return it
    return cache[(name, scale)]