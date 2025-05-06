# This file contains the class definition for 'Save' which represents
# a players save and includes data such as the player's Pokemon team,
# progression, items, etc.
from src.pokemon.pokemon import Pokemon


# Define 'Save' class

class Save:
    def __init__(
            self,
            name: str, # The trainer's name
            trainer_id: int, # The trainer's numeric ID
            created_at: int, # The timestamp this save was created at
            team: list[Pokemon], # The trainer's team
            box: list[list[Pokemon]], # The trainer's box (Pokemon in storage)
            badges: int, # The amount of badges the trainer has,
            wins: int, # The amount of battles the trainer has won
            losses: int # The amount of battles the trainer has lost
    ):
        # Initialize fields
        self.name = name
        self.trainer_id = trainer_id
        self.created_at = created_at
        self.team = team
        self.box = box
        self.badges = badges
        self.wins = wins
        self.losses = losses