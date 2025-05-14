# This file defines a class called 'Pokemon' that represents a species of
# Pokemon that has been caught by a trainer.

# Imports

from typing import Literal, cast
import uuid

from src import holder
from src.pokemon.species import Species
from src.pokemon.types.ball import Ball

from src.pokemon.types.battle_condition import BattleCondition
from src.pokemon.types.capture_data import CaptureData
from src.pokemon.types.gender import Gender
from src.pokemon.types.nature import Nature
from src.pokemon.types.stat import Stat
from src.pokemon.types.stat_table import StatTable

# Define the max level constant
MAX_LEVEL = 100

class Pokemon:
    def __init__(
            self,
            nickname: str, # The Pokemon's nickname, defaults to the species name
            egg: bool, # If this Pokemon is currently an egg
            shiny: bool, # If this Pokemon is a shiny variation (different colour)
            species: str, # The species that this Pokemon belongs to
            ability: str, # The Pokemon's ability
            tutor_machine_moves: list[list], # The moves this Pokemon has learnt through machines and move tutors
            gender: Gender, # The Pokemon's gender
            nature: Nature, # The Pokemon's nature
            ivs: StatTable, # The Pokemon's Individual Value (IV) spread
            evs: StatTable, # The Pokemon's Effort Value (EV) spread
            level: int, # The Pokemon's level
            experience: int, # The Pokemon's experience points
            friendship: int, # The Pokemon's friendship
            condition: BattleCondition, # The Pokemon's current battling condition
            capture_data: CaptureData | None # Metadata about how the Pokemon was captured and the original trainer (OT)
    ):
        # Initialize fields
        self.nickname = nickname
        self.egg = egg
        self.shiny = shiny
        self.species = species
        self.ability = ability
        self.tutor_machine_moves = tutor_machine_moves
        self.gender = gender
        self.nature = nature
        self.ivs = ivs
        self.evs = evs
        self.level = level
        self.experience = experience
        self.friendship = friendship
        self.condition = condition
        self.capture_data = capture_data

        # Initialize a UUID
        self.uuid = uuid.uuid4()

    # Define the 'get_species' function which takes the name of the species
    # and uses the holder utility to obtain the actual species object
    def get_species(self) -> Species:
        # Retrieve and return species object
        return holder.get_species(self.species)

    # Define the 'get_sprite' function that obtains the Tkinter PhotoImage of the respective sprite
    # Using the sprite type and the image scale
    def get_sprite(self, sprite_type: Literal["front", "back"], scale: tuple[int, int] = (1, 1)):
        # Delegate this function to the species get_sprite method
        return self.get_species().get_sprite(sprite_type, shiny=self.shiny, scale=scale)

    # Define a function that returns the amount of experience needed to level up
    def get_level_up_experience(self):
        # Check if Pokemon is max level
        if self.level == MAX_LEVEL:
            return 0 # Return 0
        return self.get_species().get_experience_needed(self.level + 1) # Delegate to species

    # Define a 'get_stat' method that returns the value of a Pokemon's stat
    # Formulas are from Bulbapedia, link: https://bulbapedia.bulbagarden.net/wiki/Stat
    # Using Generation III formula
    def get_stat(self, stat: Stat) -> int:
        if stat == Stat.HP: # Health uses a different formula
            return int(((2 * self.get_species().base_stats[stat.value] + self.ivs[stat.value] + (self.evs[stat.value] / 4) * self.level) / 100) + self.level + 10)
        else:
            # Initialize nature_modifier as 1
            nature_modifier = 1
            # Spread nature tuple
            increases, decreases = self.nature.value
            if stat == increases:
                nature_modifier = 1.1
            elif stat == decreases:
                nature_modifier = 0.9
            # Return calculated value of stat
            return int((((2 * self.get_species().base_stats[stat.value] + self.ivs[stat.value] + (self.evs[stat.value] / 4)) / 100) * self.level + 5) * nature_modifier)

    # Define a get_moves function that returns a list of the Pokemon's move set
    def get_moves(self) -> list[str]:
        return list(map(lambda entry: entry.name, self.condition.move_set))

    # Define a function to convert this Pokemon into a Pokemon-Showdown compatible
    # string
    # TODO Test with Nidoran-M and Nidoran-F
    def pack_string(self):
        # Initialize and empty array
        parts = []

        # Append species name
        parts.append(self.species)
        parts.append("||") # Append two separators

        # Append Pokemon's UUID
        parts.append(str(self.uuid) + "|")

        # Append Pokemon's current health
        parts.append(str(self.condition.health) + "|")

        # TODO Append current status
        parts.append("|")

        # TODO Apply sleep/freeze
        parts.append("-1|")

        # TODO Append health item
        parts.append("|")

        # Append ability
        parts.append(self.ability.replace("_", "").lower() + "|")

        # Append moves
        showdown_moves = list(map(lambda move_name: move_name.replace("_", "").lower(), self.get_moves()))
        parts.append(",".join(showdown_moves) + "|")

        # Append move PPs
        moves = self.condition.move_set
        pps = list(map(lambda move: f"{move.pp}/{move.max_pp}", moves))
        parts.append(",".join(pps) + "|")

        # Append nature
        parts.append(f"{self.nature.name.lower()}|")

        # Append EVs
        evs = list(map(lambda stat: str(self.evs[stat.value]), Stat))
        parts.append(",".join(evs) + "|")

        # Append gender
        if self.gender in [Gender.MALE, Gender.FEMALE]:
            parts.append(self.gender.name[0].upper() + "|")
        else:
            parts.append("Genderless|")

        # Append IVs
        ivs = list(map(lambda stat: str(self.ivs[stat.value]), Stat))
        parts.append(",".join(ivs) + "|")

        # Append shiny-ness
        parts.append("S|" if self.shiny else "|")

        # Append level
        parts.append(f"{self.level}|")

        # Miscellaneous fields
        parts.append(f"{self.friendship},")
        ball = self.capture_data.ball if self.capture_data is not None else Ball.POKE_BALL
        parts.append(f"{ball.name.replace("_", "")}|,")
        parts.append(",") # Skip hidden power type
        parts.append(",") # Skip GMax factor
        parts.append(",") # Skip Dynamax level
        parts.append("normal,") # Use default 'normal' tera type

        # Returned joined parts
        return "".join(parts)

    # Define a static method that takes a dictionary and returns
    # an instance of the Pokemon class
    @staticmethod
    def from_obj(obj):
        # Return an instance of Pokemon
        return Pokemon(
            obj["nickname"],
            obj["egg"],
            obj["shiny"],
            obj["species"],
            obj["ability"],
            obj["tutor_machine_moves"],
            Gender.of(obj["gender"]),
            Nature.of(obj["nature"]),
            cast(StatTable, obj["ivs"]),
            cast(StatTable, obj["evs"]),
            obj["level"],
            obj["experience"],
            obj["friendship"],
            BattleCondition.of(obj["condition"]),
            cast(CaptureData, obj["capture_data"]),
        )