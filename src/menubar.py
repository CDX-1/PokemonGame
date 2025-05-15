# This file contains a simple method that will take the Tkinter root and
# add a menubar to it

# Imports

import tkinter as tk
from tkinter import messagebox, scrolledtext

import os
import platform
import subprocess

import src.resources as resources
from src import holder
from src.game.battle_client import BattleEvent, BattleClient
from src.utils.font import get_bold_font
from src.windows.abstract.TopLevelWindow import TopLevelWindow

# A utility function to open folders
def open_folder(path: str):
    # Define exact path to folder
    abs_path = os.path.abspath(path)
    # Check current operating system (different OS's have different ways of
    # programmatically opening folders)
    if platform.system() == "Windows":
        os.startfile(abs_path)
    elif platform.system() == "Darwin":  # MacOS
        subprocess.run(["open", abs_path])
    else:  # Linux
        subprocess.run(["xdg-open", abs_path])

# Open saves folder callback
def open_saves_folder():
    # Use the 'open_folder' function
    open_folder("saves")

# Open packs folder callback
def open_packs_folder():
    # Use the 'open_folder' function
    open_folder("packs")

# Open assets folder callback
def open_assets_folder():
    # Use the 'open_folder' function
    open_folder("assets")

# About game callback
def about():
    # Create a top level window
    window = TopLevelWindow.create_basic_window("About", width=160, height=100)
    # Create a centered container frame
    frame = tk.Frame(window)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # Add header text to frame
    header = tk.Label(frame, text="Pokemon Game", font=get_bold_font())
    header.pack()
    # Add a created by label
    created_by = tk.Label(frame, text="Created by Awsaf Syed")
    created_by.pack()
    # Start window loop
    window.mainloop()

# Config game callback
def config():
    # Create a top level window
    window = TopLevelWindow.create_basic_window("Config", width=200, height=150)
    # Create a centered container frame
    frame = tk.Frame(window)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    # Add header text to frame
    header = tk.Label(frame, text="Configure", font=get_bold_font())
    header.pack()

    # Add configurator for shiny odds
    config_shiny_prefix = tk.Label(frame, text="Shiny Odds")
    config_shiny_prefix.pack()

    # Create variable for shiny odds
    shiny_odds_var = tk.StringVar(value=resources.SHINY_ODDS)

    # Add entry widget for shiny odds
    config_shiny_entry = tk.Entry(frame, textvariable=shiny_odds_var)
    config_shiny_entry.pack()

    # Add configurator for hidden ability odds
    config_hidden_ability_prefix = tk.Label(frame, text="Hidden Ability Odds")
    config_hidden_ability_prefix.pack()

    # Create variable for hidden ability odds
    hidden_ability_odds_var = tk.StringVar(value=resources.HIDDEN_ABILITY_ODDS)

    # Add entry widget for hidden ability odds
    config_hidden_ability_entry = tk.Entry(frame, textvariable=hidden_ability_odds_var)
    config_hidden_ability_entry.pack()

    # Create callback function for update button
    def update():
        # Ensure shiny odds and hidden ability odds are valid doubles
        try:
            float(config_shiny_entry.get())
            float(config_hidden_ability_entry.get())
        except ValueError:
            # Inform user of invalid entries
            messagebox.showerror("Invalid Entry", "You must ensure that inputs are valid")
            # Exit callback
            return

        # Update values
        resources.SHINY_ODDS = float(shiny_odds_var.get())
        resources.HIDDEN_ABILITY_ODDS = float(hidden_ability_odds_var.get())

        # Destroy top level window
        window.destroy()

    # Add update button
    update_button = tk.Button(frame, text="Update", command=update)
    update_button.pack()

# Debug battle callback
def debug_battle():
    # Create a top level window
    window = TopLevelWindow.create_basic_window("Battle Logs", width=1000, height=500)

    def render(battle: BattleClient):
        nonlocal window
        # Destroy the window
        window.destroy()

        # Create a top level window
        window = TopLevelWindow.create_basic_window("Battle Logs", width=1000, height=500)

        # Create a frame to hold logs and scrollbar
        log_frame = tk.Frame(window)
        log_frame.pack(fill=tk.BOTH, expand=True)

        # ScrolledText widget for battle logs
        log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        log_text.pack(fill=tk.BOTH, expand=True)

        # Frame for input and send button
        input_frame = tk.Frame(window)
        input_frame.pack(fill=tk.X)

        # Entry widget for commands
        cmd_entry = tk.Entry(input_frame)
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), pady=5)

        # A function to send commands
        def send_command(cmd, entry_widget):
            # Send the command
            battle.send_command_unsafe(cmd)
            # Clear entry after sending
            entry_widget.delete(0, tk.END)

        # A function to append messages to the log
        def append_msg(message):
            # Enable, insert message, then disable to make read-only
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, message + "\n")
            log_text.see(tk.END)  # scroll to end
            log_text.config(state=tk.DISABLED)

        # Send button
        send_btn = tk.Button(input_frame, text="Send",
                             command=lambda: send_command(cmd_entry.get(), cmd_entry))
        send_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        # Load existing logs
        for message in battle.logs:
            append_msg(message)

        # Listen for new messages
        battle.on(BattleEvent.LOG, append_msg)

    # Check if there is an active battle
    if holder.battle is None:
        # Placeholder label if no battle
        no_battle_label = tk.Label(window, text="No active battle. Re-open window to load new battles.", wraplength=400)
        no_battle_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Callback to wait for a battle
        def check_for_battle(found_callback):
            if holder.battle is not None:
                no_battle_label.destroy()
                found_callback(holder.battle)
            else:
                holder.root.after(500, lambda: check_for_battle(found_callback))

        # Start polling
        check_for_battle(render)
    else:
        render(holder.battle)

# Define the 'setup_menubar' function that takes a parent
def setup_menubar(parent: tk.Tk):
    # Create menubar
    menubar = tk.Menu(parent)
    parent.config(menu=menubar)

    # Create 'Game' tab
    game_tab = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Game", menu=game_tab)
    # Add about button
    game_tab.add_command(label="About", command=about)
    # Add open saves, open packs, and open assets buttons
    game_tab.add_command(label="Open Saves Folder", command=open_saves_folder)
    game_tab.add_command(label="Open Packs Folder", command=open_packs_folder)
    game_tab.add_command(label="Open Assets Folder", command=open_assets_folder)
    # Add exit button
    game_tab.add_command(label="Exit", command=parent.destroy)

    # Create 'Cheats' tab
    cheats_tab = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Cheats", menu=cheats_tab)
    # Add config button
    cheats_tab.add_command(label="Config", command=config)

    # Create 'Debug' tab
    debug_tab = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label="Debug", menu=debug_tab)
    # Add a battle console button
    debug_tab.add_command(label="Open Battle Console", command=debug_battle)