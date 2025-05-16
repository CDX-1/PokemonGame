# This following few lines is to make this code executable through IDLEs GUI
# Import os and sys for fixes
import os
import sys

# Check if the current working directory is the same as the parent
# of this file
if os.path.abspath(os.getcwd()) == os.path.abspath("./"):
    # Add the parent folder to the path so modules can be imported correctly
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

# This is the main file that is executed when the program is run
# This file coordinates the showing of different windows and contains
# the main functions

# Imports

import tkinter as tk
from tkinter import messagebox
import json
import os

from src.menubar import setup_menubar
from src.pack_processor import LoadedPack, load_pack
from src.utils import requests
from src.windows.main_menu import MainMenu
from src.windows.navigator import Navigator
import src.utils.images as images
import src.resources as resources

# Define the main function
def main():
    import src.holder as holder
    # Create the Tkinter root
    root = tk.Tk()
    holder.root = root
    # Set the title of the root window
    root.title("Pokemon")
    # Set size of the root window
    root.geometry("700x400")
    # Make root window not resizable
    root.resizable(False, False)

    # Ensure /packs/ and /saves/ folder exists
    os.makedirs("packs", exist_ok=True)
    os.makedirs("saves", exist_ok=True)
    os.makedirs("assets", exist_ok=True)


    # Keep looping until the 'packs' folder is no longer empty
    while len(os.listdir("packs")) == 0:
        # Show dialogue to inform user something is happening
        messagebox.showinfo("Downloading", "We're currently downloading some content! If this is your " +\
                            "first time using this program, please wait until the main menu loads. You " +\
                            "must click 'OK'")
        # Download data
        download()

    # Create a shutdown callback that will be run when the program shuts down
    def shutdown_callback():
        # Check if there is an active save
        if holder.save is not None:
            # Save to disk
            holder.save.write()
        # Destroy root
        root.destroy()

    # Attach shutdown callback to the WM_DELETE_WINDOW event which is called when a window is destroyed
    root.protocol("WM_DELETE_WINDOW", shutdown_callback)

    # Setup the menubar
    setup_menubar(root)

    # Load the main images through the 'load_images' function
    # which is defined later
    load_images()

    # Load the generation 1 pack
    loaded_pack = load_pack("packs/gen-1.json")

    # Load all Pokemon sprites through the 'load_sprites' function
    # which is defined later
    load_sprites(loaded_pack)

    # Provide loaded pack to the holder
    holder.pack = loaded_pack

    # Define a callback function to handle when the main menu is complete
    def on_save_select():
        # Draw the navigator as main menu will only exit once a save is selected
        Navigator(root).draw()

    # Draw the main menu frame
    MainMenu(root, on_save_select).draw()

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

    # Load button icons
    images.load_image("encounter", f"assets/buttons/encounter_icon.png")
    images.load_image("bag", f"assets/buttons/bag_icon.png")
    images.load_image("box", f"assets/buttons/box_icon.png")
    images.load_image("shop", f"assets/buttons/shop_icon.png")
    images.load_image("swap", f"assets/buttons/swap_icon.png")

    # Load type icons
    for pokemon_type in ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "fire", "water",
                         "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"]:
        images.load_image(pokemon_type, f"assets/types/{pokemon_type}.png")

# Define the download function
def download():
    # Download assets
    requests.download(resources.assets, "assets/", unzip=True)
    print(f"Downloaded and unzipped {resources.assets}")

    # Iterate all packs
    for name, pack_data in resources.packs.items():
        # Spread pack_data
        pack_name, pack_url = pack_data
        # Print that the pack has started downloading
        print(f"Downloading and unzipping {pack_url}...")
        # Use the requests utility to download the pack from the URL, unzip it and put it in the packs/ folder
        requests.download(pack_url, "packs/", unzip=True)
        # Print that the pack has finished downloading and unzipping
        print(f"Downloaded and unzipped {pack_url}")

        # Iterate all packs in pack folder
        for pack in os.listdir("packs/"):
            # Open pack file in read (R) mode with the file referenced as 'f'
            with open(f"packs/{pack}", 'r') as f:
                # Load JSON as Python object
                data = json.load(f)
                # Iterate all Pokemon species
                for species in data["species"]:
                    # Parse species name
                    species_name = species["name"]
                    # Parse sprite table
                    sprites = species["sprites"]
                    regular_sprites = sprites["regular"]
                    shiny_sprites = sprites["shiny"]
                    # Download all regular sprites (front & back) to assets
                    requests.download(regular_sprites["front"], f"assets/{species_name}/regular/front.png")
                    requests.download(regular_sprites["back"], f"assets/{species_name}/regular/back.png")
                    # Download all shiny sprites (front & back) to assets
                    requests.download(shiny_sprites["front"], f"assets/{species_name}/shiny/front.png")
                    requests.download(shiny_sprites["back"], f"assets/{species_name}/shiny/back.png")
                    # Inform user that images were downloaded
                    print(f"Downloaded sprite assets for: {species_name} ({pack})")

        # Inform user that asset download is complete
        print("Finished downloaded assets")

# Ensure that this file is being directly executed and not imported
# as a module for another file
if __name__ == '__main__':
    # Call the main function
    main()