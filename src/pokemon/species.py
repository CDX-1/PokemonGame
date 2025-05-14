# This file contains the class definition for a species of Pokemon including
# information regarding its type, gender ratio, sprite resource links, etc.
# This file also defines helper classes such as 'GenderRatio' to properly
# separate this class.

# Imports

from typing import TypedDict, cast, Literal

from src.pokemon.types.battle_condition import BattleCondition, BattleMove
from src.pokemon.types.capture_data import CaptureData
from src.pokemon.types.egg_groups import EggGroup
from src.pokemon.types.evolution import Evolution
from src.pokemon.types.gender import Gender
from src.pokemon.types.growth_rate import GrowthRate
from src.pokemon.types.learnable_move import LearnableMove
from src.pokemon.types.nature import Nature
from src.pokemon.types.stat import Stat
from src.pokemon.types.stat_table import OptionalStatTable, StatTable
from src.utils import images
import src.resources as resources

import random

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

    # Define the 'get_sprite' function that obtains the Tkinter PhotoImage of the respective sprite
    # Using the sprite type, shiny status, and the image scale
    def get_sprite(self, sprite_type: Literal["front", "back"], shiny: bool = False, scale: tuple[int, int] = (1, 1)):
        # Check if Pokemon is shiny
        if shiny:
            # Declare sprite_variant as shiny variant
            sprite_variant = "shiny"
        else:
            # Declare sprite_variant as regular variant
            sprite_variant = "regular"
        # Return the sprite PhotoImage instance using the images utility with the provided scale
        return images.get_image(f"{self.name}_{sprite_variant}_{sprite_type}", scale=scale)

    # Define the 'get_known_moves' which returns a list of the moves
    # this species can learn through level up at this current level
    def get_known_moves(self, level: int) -> list[str]:
        # Initialize an empty list of known moves
        known_moves = []
        # Iterate this species learnable moves
        for move in self.moves:
            # Check if this move can be learnt by level up
            if move["level"] is not None:
                # Check if Pokemon's level is high enough
                if level >= move["level"]:
                    # Append move name to list of known moves
                    known_moves.append(move["name"])
        # Return list of known moves
        return known_moves

    # Define a function that returns the amount of experience needed to level up
    def get_experience_needed(self, next_level: int):
        return self.growth_rate.get_experience_needed(next_level) # Delegate to growth rate

    # Define a method called 'spawn' that creates a fresh
    # instance of a Pokemon of this species with realistic stats
    # that takes a primitive integer or a range of integers
    def spawn(self, levels: int | range, capture_data: CaptureData | None = None, is_egg: bool = False, force_shiny: bool = False):
        # Import Pokemon & holder here to avoid circular import error
        from src.pokemon.pokemon import Pokemon
        from src import holder

        # Check if 'levels' is a primitive integer
        if isinstance(levels, int):
            level = levels
        else: # 'levels' is a range, so select a random integer in the range
            level = random.choice(levels)

        # Check if the Pokemon should be shiny
        if force_shiny:
            is_shiny = True
        elif random.random() < resources.SHINY_ODDS: # Otherwise check shiny odds
            is_shiny = True
        else: is_shiny = False # Default is_shiny to false

        # Check if hidden ability should be given
        if len(self.abilities["hidden"]) == 0:
            is_hidden_ability = False # Set to false if species does not have a hidden ability
        elif random.random() < resources.HIDDEN_ABILITY_ODDS:
            is_hidden_ability = True # Set to true if odds are met
        else: is_hidden_ability = False # Default is_hidden_ability to false

        # Check if using hidden ability
        if is_hidden_ability:
            # Set selected ability to species hidden ability
            ability = self.abilities["hidden"][0]
        else:
            # Otherwise set ability to random ability from regular abilities
            ability = random.choice(self.abilities["regular"])

        # Check if Pokemon is genderless
        if self.gender_ratio is None:
            gender = Gender.GENDERLESS
        else:
            # Calculate gender using randomness
            if random.random() < self.gender_ratio["male"]:
                gender = Gender.MALE # Set gender to male
            else:
                gender = Gender.FEMALE # Otherwise, set gender to female

        # Get the moves this Pokemon knows
        known_moves = self.get_known_moves(level)
        # Shuffle known moves
        random.shuffle(known_moves)

        # Build the instance of the Pokemon
        pokemon = Pokemon(
            nickname=self.name.title(),
            egg=is_egg,
            shiny=is_shiny,
            species=self.name,
            ability=ability,
            tutor_machine_moves=[],
            gender=gender,
            nature=random.choice(list(Nature)), # Random nature
            ivs=StatTable( # IVs are random and between 0 and 31
                hp=random.randint(0, 31),
                attack=random.randint(0, 31),
                special_attack=random.randint(0, 31),
                defense=random.randint(0, 31),
                special_defense=random.randint(0, 31),
                speed=random.randint(0, 31),
            ),
            evs=StatTable( # EVs are all zero by default
                hp=0,
                attack=0,
                special_attack=0,
                defense=0,
                special_defense=0,
                speed=0
            ),
            level=level,
            experience=0,
            friendship=self.base_friendship,
            condition=None,
            capture_data=capture_data
        )

        # Create a blank 'healthy' condition
        pokemon.condition = BattleCondition(
            health=pokemon.get_stat(Stat.HP),
            status_condition=None,
            confused=False,
            held_item=None,
            move_set=list(map(
                lambda move_name: BattleMove(
                    move_name,
                    holder.get_move(move_name).pp,
                    holder.get_move(move_name).pp,
                    False
                ),
                known_moves[:4]
            )),
            stat_changes=OptionalStatTable()
        )

        # Return Pokemon instance
        return pokemon