# The BallHandler class is a functional class meaning it just contains
# a callback function that will be called whenever a certain ball type is
# used.

# The Ball class is an enum that contains every implemented ball type, and
# it's respective handler.

# Imports

from enum import Enum

# Define BallHandler class

class BallHandler:
    # Wraps a callback function that takes in a catch context and returns the ball's catch rate modifier
    def __init__(self, handler):
        # Initialize fields
        self.handler = handler

# Define Ball class

class Ball(Enum):
    POKE_BALL = BallHandler(lambda ctx: 1) # Standard Pokeball, x1
    GREAT_BALL = BallHandler(lambda ctx: 1.5) # Better Pokeball, x1.5
    ULTRA_BALL = BallHandler(lambda ctx: 2) # Good Pokeball, x2
    MASTER_BALL = BallHandler(lambda ctx: 255) # Perfect Pokeball, x255 (100% catch rate)
    QUICK_BALL = BallHandler(lambda ctx: 5 if ctx.turn == 1 else 1) # Quick Ball, x5 on turn 1, otherwise x1

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Iterate all enumerations
        for entry in Ball:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value.lower():
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid ball: {value}")