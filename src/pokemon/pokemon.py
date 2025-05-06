# This file defines a class called 'Pokemon' that represents a species of
# Pokemon that has been caught by a trainer.

# Imports

from src.pokemon.species import Species
from src.pokemon.types.battle_condition import BattleCondition
from src.pokemon.types.capture_data import CaptureData
from src.pokemon.types.gender import Gender
from src.pokemon.types.nature import Nature
from src.pokemon.types.stat_table import StatTable

class Pokemon:
    def __init__(
            self,
            nickname: str, # The Pokemon's nickname, defaults to the species name
            egg: bool, # If this Pokemon is currently an egg
            shiny: bool, # If this Pokemon is a shiny variation (different colour)
            species: Species, # The species that this Pokemon belongs to
            ability: str, # The Pokemon's ability
            gender: Gender, # The Pokemon's gender
            nature: Nature, # The Pokemon's nature
            ivs: StatTable, # The Pokemon's Individual Value (IV) spread
            evs: StatTable, # The Pokemon's Effort Value (EV) spread
            level: int, # The Pokemon's level
            experience: int, # The Pokemon's experience points
            friendship: int, # The Pokemon's friendship
            condition: BattleCondition, # The Pokemon's current battling condition
            capture_data: CaptureData # Metadata about how the Pokemon was captured and the original trainer (OT)
    ):
        # Initialize fields
        self.nickname = nickname
        self.egg = egg
        self.shiny = shiny
        self.species = species
        self.ability = ability
        self.gender = gender
        self.nature = nature
        self.ivs = ivs
        self.evs = evs,
        self.level = level,
        self.experience = experience
        self.friendship = friendship
        self.condition = condition
        self.capture_data = capture_data