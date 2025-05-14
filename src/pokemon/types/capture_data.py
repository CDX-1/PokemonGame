# This file contains the CaptureData class which stores information
# about how a Pokemon was caught by the player such as which Pokeball
# was used and the name and ID of the trainer.

# Imports

from src.pokemon.types.ball import Ball

# Define the 'CaptureData' class

class CaptureData:
    def __init__(
            self,
            ball: Ball, # The Pokeball that was used to catch this Pokemon
            original_trainer: str, # The name of the original trainer
            original_trainer_id: int # the ID of the original trainer
    ):
        # Initialize fields
        self.ball = ball
        self.original_trainer = original_trainer
        self.original_trainer_id = original_trainer_id

    # Define a static 'of' function that will convert a bland dictionary to an instance of this object
    @staticmethod
    def of(obj):
        return CaptureData(
            Ball.of(obj["ball"]),
            obj["original_trainer"],
            obj["original_trainer_id"]
        )