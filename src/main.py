# This is the main file that is executed when the program is run
# This file coordinates the showing of different windows and contains
# the main function.

# Imports

import tkinter as tk
import os

from src.windows.pack_downloader import PackDownloader
import src.utils.images as images

# Define the main function

def main():
    # Create the Tkinter root
    root = tk.Tk()
    # Set the title of the root window
    root.title("Pokemon")
    # Set size of the root window
    root.geometry("400x400")
    # Make root window not resizable
    root.resizable(False, False)

    # Load the main images through the 'load_images' function
    # which is defined later
    load_images()

    # Keep looping until the 'packs' folder is no longer empty
    while len(os.listdir("packs")) == 0:
        # Prompt the user with the 'PackDownloader' window
        PackDownloader(root).draw().wait()

    # Execute the root main loop
    root.mainloop()

# Define the 'load_images' function to load the most important image assets

def load_images():
    images.load_image("logo", "assets/logo.png") # Logo

# Ensure that this file is being directly executed and not imported
# as a module for another file
if __name__ == '__main__':
    # Call the main function
    main()