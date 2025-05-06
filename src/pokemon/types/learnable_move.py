# This file defines a class called LearnableMove which is used to declare
# moves a Pokemon can learn and the way it can learn it such as through level
# up, a technical machine, or through a move tutor.

# Define the 'LearnableMove' class

class LearnableMove:
    def __init__(
            self,
            name: str, # The name of the move
            level: int | None, # The level that the Pokemon learns this move at, if any
            machine: bool, # Whether this move can be taught to this Pokemon through a technical machine or not
            tutor: bool # Whether this move can be taught to this Pokemon through a move tutor or not
    ):
        # Initialize fields
        self.name = name
        self.level = level
        self.machine = machine
        self.tutor = tutor
