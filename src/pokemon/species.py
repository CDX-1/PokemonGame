# This file contains the class definition for a species of Pokemon including
# information regarding its type, gender ratio, sprite resource links, etc.
# This file also defines helper classes such as 'GenderRatio' to properly
# separate this class.

# Imports

from typing import TypedDict, cast

from src.pokemon.types.egg_groups import EggGroup
from src.pokemon.types.evolution import Evolution
from src.pokemon.types.growth_rate import GrowthRate
from src.pokemon.types.learnable_move import LearnableMove
from src.pokemon.types.stat_table import OptionalStatTable, StatTable

# Define an 'Abilities' dictionary class which separates a Pokemon's regular abilities
# and its more rare hidden abilities of which a species only has one of

class Abilities(TypedDict):
    regular: list[str]
    hidden: list[str]

# Define a 'GenderRatio' dictionary class that contains the chance that this
# Pokemon can be a male vs a female.

class GenderRatio(TypedDict):
    male: float
    female: float

# Define a 'SpritePair' dictionary class that separates resource links for a front
# view of the Pokemon's sprite and a back view of the Pokemon's sprite

class SpritePair(TypedDict):
    front: str # Resource URL for the front view
    back: str # Resource URL for the back view

# Define a 'SpriteTable' dictionary class that separates the Pokemon's sprite pairs
# for regular variations of the Pokemon and shiny variations of the Pokemon.

class SpriteTable(TypedDict):
    regular: SpritePair # Regular variation SpritePair
    shiny: SpritePair # Shiny variation SpritePair

# Define the 'Species' class

class Species:
    def __init__(
            self,
            dex_id: int, # The unique numeric ID for the species
            id: str, # The code name/code ID for the species
            name: str, # A cleaner, more presentable name for the species
            desc: str, # A short description of the species
            genus: str, # An even shorter one-line description of the species
            types: list[str], # The type(s) of the species, at most two
            abilities: Abilities, # This species abilities
            evolutions: list[Evolution], # The possible evolutions for this species
            height: float, # The height of this species in meters
            weight: float, # The weight of this species in kilograms
            ev_yield: OptionalStatTable, # The effort values (EV) that this species awards on defeat
            catch_rate: int, # The catch rate of this species, capping out at 255 for a 100% catch rate
            base_friendship: int, # The friendship level of this species when it is caught
            base_exp: int, # The amount of experience that this species awards on defeat
            growth_rate: GrowthRate, # The growth rate of this species (how fast it levels up)
            egg_groups: list[EggGroup], # The egg groups that this species falls into (maximum of 2)
            egg_cycles: int, # The amount of egg cycles that's needed to hatch an egg of this species
            gender_ratio: GenderRatio | None, # The gender ratio of this species
            base_stats: StatTable, # The base stats of this species
            moves: list[LearnableMove], # The moves that this species can learn
            sprites: SpriteTable # The resource URLs for this species sprites
    ):
        # Initialize fields
        self.dex_id = dex_id
        self.id = id
        self.name = name
        self.desc = desc
        self.genus = genus
        self.types = types
        self.abilities = abilities
        self.evolutions = evolutions
        self.height = height
        self.weight = weight
        self.ev_yield = ev_yield
        self.catch_rate = catch_rate
        self.base_friendship = base_friendship
        self.base_exp = base_exp
        self.growth_rate = growth_rate
        self.egg_groups = egg_groups
        self.egg_cycles = egg_cycles
        self.gender_ratio = gender_ratio
        self.base_stats = base_stats
        self.moves = moves
        self.sprites = sprites

    # Define a static method that takes a dictionary and returns
    # an instance of the species class
    @staticmethod
    def from_obj(obj):
        # Return instance of species
        return Species(
            obj["dex_id"],
            obj["id"],
            obj["name"],
            obj["desc"],
            obj["genus"],
            obj["types"],
            abilities=Abilities(
                regular=obj["abilities"]["regular"],
                hidden=obj["abilities"]["hidden"],
            ),
            evolutions=list(map(lambda entry: cast(entry, Evolution), obj["evolutions"])), # Cast each sub-dictionary to an Evolution
            height=obj["height"],
            weight=obj["weight"],
            ev_yield=cast(OptionalStatTable, obj["ev_yield"]), # Cast the sub-dictionary to an OptionalStatTable
            catch_rate=obj["catch_rate"],
            base_friendship=obj["base_friendship"],
            base_exp=obj["base_exp"],
            growth_rate=GrowthRate.of(obj["growth_rate"]), # Obtain the actual GrowthRate instance
            egg_groups=list(map(lambda entry: EggGroup.of(entry), obj["egg_groups"])), # Obtain the actual EggGroup instances and convert to list
            egg_cycles=obj["egg_cycles"],
            gender_ratio=cast(GenderRatio, obj["gender_ratio"]), # Cast the sub-dictionary to a GenderRatio
            base_stats=cast(StatTable, obj["base_stats"]), # Cast the sub-dictionary to a StatTable
            moves=list(map(lambda entry: cast(LearnableMove, entry), obj["moves"])), # Cast each learnable move sub-dictionary to a LearnableMove
            sprites=cast(SpriteTable, obj["sprites"]) # Cast the sprites sub-dictionary to a SpriteTable
        )