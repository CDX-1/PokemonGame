# This is the main file that is executed when the program is run
# This file coordinates the showing of different windows and contains
# the main function.

# Imports

import tkinter as tk
import os

from src.menubar import setup_menubar
from src.pack_processor import LoadedPack, load_pack
from src.windows.main_menu import MainMenu
from src.windows.pack_downloader import PackDownloader
import src.utils.images as images
import src.holder as holder

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

    # Setup the menubar
    setup_menubar(root)

    # Ensure /packs/ and /saves/ folder exists
    os.makedirs("packs", exist_ok=True)
    os.makedirs("saves", exist_ok=True)

    # Load the main images through the 'load_images' function
    # which is defined later
    load_images()

    # Keep looping until the 'packs' folder is no longer empty
    while len(os.listdir("packs")) == 0:
        # Prompt the user with the 'PackDownloader' window
        PackDownloader(root).draw().wait()

    # Load the generation 1 pack
    loaded_pack = load_pack("packs/gen-1.json")

    # Load all Pokemon sprites through the 'load_sprites' function
    # which is defined later
    load_sprites(loaded_pack)

    # Provide loaded pack to the holder
    holder.pack = loaded_pack

    # Draw the main menu frame
    MainMenu(root).draw()

    # Execute the root main loop
    root.mainloop()

# Define the 'load_images' function to load the most important image assets
def load_images():
    images.load_image("logo", "assets/logo.png") # Load logo
    # Iterate all Poke Ball types
    for item in ["poke", "great", "ultra", "master", "quick"]:
        # Load Pokeball asset
        images.load_image(f"item_{item}_ball", f"assets/items/{item}_ball.png")

# Define the 'load_sprites' function to preload all Pokemon sprites with a given loaded pack
def load_sprites(pack: LoadedPack):
    # Iterate all the species in the pack
    for species in pack.species:
        # Load species sprites from disk
        images.load_image(f"{species.name}_regular_front", f"assets/{species.name}/regular/front.png") # Regular Front
        images.load_image(f"{species.name}_regular_back", f"assets/{species.name}/regular/back.png") # Regular Back
        images.load_image(f"{species.name}_shiny_front", f"assets/{species.name}/shiny/front.png") # Shiny Front
        images.load_image(f"{species.name}_shiny_back", f"assets/{species.name}/shiny/back.png") # Shiny Back

# Ensure that this file is being directly executed and not imported
# as a module for another file
if __name__ == '__main__':
    # Call the main function
    main()