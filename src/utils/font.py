# This file provides utility functions to get different fonts for Tkinter

# Imports

import tkinter as tk
import tkinter.font as font

# Define 'get_font' function which returns a tuple that can be used as a font
def get_font() -> tuple[str, int, str]:
    # Retrieve the default font
    default_font = font.nametofont("TkDefaultFont")
    return default_font.name, default_font.cget("size"), ""

# Define 'get_title_font' function which returns a tuple that can be used as a font
def get_title_font() -> tuple[str, int, str]:
    # Retrieve the default font
    default_font = font.nametofont("TkDefaultFont")
    return default_font.name, default_font.cget("size") + 8, "bold"

# Define 'get_mono_font' function which returns a tuple that can be used as a font
def get_mono_font() -> tuple[str, int, str]:
    # Retrieve the default font
    default_font = font.nametofont("TkDefaultFont")
    return "Courier New", default_font.cget("size"), ""

# Define 'get_bold_font' function which returns a tuple that can be used as a font
def get_bold_font() -> tuple[str, int, str]:
    # Retrieve the default font
    default_font = font.nametofont("TkDefaultFont")
    return default_font.name, default_font.cget("size"), "bold"

# Define 'get_underline_font' function which returns a tuple that can be used as a font
def get_underline_font() -> tuple[str, int, str]:
    # Retrieve the default font
    default_font = font.nametofont("TkDefaultFont")
    return default_font.name, default_font.cget("size"), "underline"