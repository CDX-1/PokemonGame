# This file contains the class definition for 'Save' which represents
# a players save and includes data such as the player's Pokemon team,
# progression, items, etc.

# Imports

import json

from src.generator.tools.purifier import purify_obj
from src.pokemon.pokemon import Pokemon

# Define 'Save' class
class Save:
    def __init__(
            self,
            name: str, # The trainer's name
            trainer_id: int, # The trainer's numeric ID
            created_at: int, # The timestamp this save was created at
            starter: str, # The starter the trainer has selected
            route: int, # The route that the player is on
            team: list[Pokemon], # The trainer's team
            box: list[list[Pokemon]], # The trainer's box (Pokemon in storage)
            badges: int, # The amount of badges the trainer has,
            bag: dict[str, int], # The player's bag/items
            yen: int, # The amount of money the trainer has
            wins: int, # The amount of battles the trainer has won
            losses: int # The amount of battles the trainer has lost
    ):
        # Initialize fields
        self.name = name
        self.trainer_id = trainer_id
        self.created_at = created_at
        self.starter = starter
        self.route = route
        self.team = team
        self.box = box
        self.badges = badges
        self.bag = bag
        self.yen = yen
        self.wins = wins
        self.losses = losses

    # Define a function to consume an item from the bag
    def consume_item(self, item: str, amount: int = 1):
        # Check if item is in the bag
        if item in self.bag:
            # Check if deduction would be less than or equal to 0
            if self.bag[item] - amount <= 0:
                # Remove item
                self.bag.pop(item)
            else:
                # Decrease amount
                self.bag[item] -= amount

    # Define the write function which will write this save file to disk
    def write(self):
        # Write the save to disk
        # Open the save file in write (W) mode
        with open(f"saves/{self.trainer_id}-{self.created_at}.json", "w") as f:
            # Write purified save object to file
            json.dump(purify_obj(self), f, indent=4)
        # Log that the save was written to disk
        print(f"Wrote save: '{self.trainer_id}-{self.created_at}.json' to disk")

    # Define a static method that takes a dictionary and returns
    # an instance of the save class
    @staticmethod
    def from_obj(obj):
        # Return instance of save
        return Save(
            obj["name"],
            obj["trainer_id"],
            obj["created_at"],
            obj["starter"],
            obj["route"],
            list(map(lambda entry: Pokemon.from_obj(entry), obj["team"])), # Map each Pokemon from dictionary in the team to a Pokemon object
            list(map(lambda box: list(map(lambda entry: Pokemon.from_obj(entry), box)), obj["box"])), # Map each Pokemon from dictionary in the boxes to a Pokemon object
            obj["badges"],
            obj["bag"],
            obj["yen"],
            obj["wins"],
            obj["losses"]
        )