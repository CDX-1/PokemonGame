# This file defines a class that represents all the information associated
# with a move. Ranging from the move's type to chance to cause the target to
# flinch.

# Imports

from typing import cast

from src.pokemon.types.damage_class import DamageClass
from src.pokemon.types.move_ailment import MoveAilment
from src.pokemon.types.move_category import MoveCategory
from src.pokemon.types.move_target import MoveTarget
from src.pokemon.types.stat_table import BattleStatTable

# Define the 'Move' class
class Move:
    def __init__(
            self,
            id: int, # Unique numeric ID of the move
            name: str, # The move's name
            desc: str, # A short description of the move
            type: str, # The move's type
            accuracy: int | None, # The accuracy of the move, none means that the move will never miss
            effect_chance: int, # The chance that the move will inflict its effect
            pp: int, # The max power points (PP) of the move
            priority: int, # The priority order of the move (ranging from -8 to 8)
            power: int | None, # The move's base power, none if it is a non-damaging move
            damage_class: DamageClass, # The damage class of the move (physical, special, status)
            stat_changes: BattleStatTable, # The stat changes the move can cause
            target: MoveTarget, # The move's target
            ailment: MoveAilment, # The ailment that the move can cause (or MoveAilment.NONE)
            category: MoveCategory, # The category that this move falls into
            min_hits: int | None, # The minimum amount of hits this move will do, if it is a multi-hit move
            max_hits: int | None, # The maximum amount of hits this move will do, if it is a multi-hit move
            max_turns: int | None, # The maximum amount of turns the effects of this move will last, if it lasts multiple turns
            drain: float | None, # The percent of the target's health to drain
            healing: float | None, # The percent of the total damage dealt by this move to heal the user
            crit_chance: float, # The chance that this move lands a critical hit (1.5x damage)
            ailment_chance: float, # The chance that this move inflicts its ailment (if it has one)
            flinch_chance: float, # The chance that this move will cause the target to flinch
            stat_chance: float # The chance that this move will perform stat changes
    ):
        # Initialize fields
        self.id = id
        self.name = name
        self.desc = desc
        self.type = type
        self.accuracy = accuracy
        self.effect_chance = effect_chance
        self.pp = pp
        self.priority = priority
        self.power = power
        self.damage_class = damage_class
        self.stat_changes = stat_changes
        self.target = target
        self.ailment = ailment
        self.category = category
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.max_turns = max_turns
        self.drain = drain
        self.healing = healing
        self.crit_chance = crit_chance
        self.ailment_chance = ailment_chance
        self.flinch_chance = flinch_chance
        self.stat_chance = stat_chance

    # Define a format function that formats the name of this move cleanly
    def format(self):
        return self.name.replace("_", " ").title()

    # Define a static method, 'from_obj,' that takes a dictionary
    # and converts it into this class
    @staticmethod
    def from_obj(obj):
        # Return instance of 'Move'
        return Move(
            obj["id"],
            obj["name"],
            obj["desc"],
            obj["type"],
            obj["accuracy"],
            obj["effect_chance"],
            obj["pp"],
            obj["priority"],
            obj["power"],
            DamageClass.of(obj["damage_class"]),
            cast(BattleStatTable, obj["stat_changes"]),
            MoveTarget.of(obj["target"]),
            MoveAilment.of(obj["ailment"]),
            MoveCategory.of(obj["category"]),
            obj["min_hits"],
            obj["max_hits"],
            obj["max_turns"],
            obj["drain"],
            obj["healing"],
            obj["crit_chance"],
            obj["ailment_chance"],
            obj["flinch_chance"],
            obj["stat_chance"]
        )