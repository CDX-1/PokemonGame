# Contains classes pertaining to the condition/state of a Pokemon
# during battle, specifically volatile metadata (doesn't persist
# after the battle is over).

from src.pokemon.types.stat_table import OptionalStatTable
from src.pokemon.types.status_condition import StatusCondition

# Define BattleMove class
# Represents a Pokemon's move during battle

class BattleMove:
    def __init__(
            self,
            name: str, # Move's name
            pp: int, # Move's current power points (PP)
            max_pp: int, # Move's max power points (PP)
            disabled: bool # Whether the move has been disabled by an ability or move
    ):
        # Initialize fields
        self.name = name
        self.pp = pp
        self.max_pp = max_pp
        self.disabled = disabled

# Define BattleCondition class
# Represents the state of a Pokemon during battle

class BattleCondition:
    def __init__(
            self,
            health: int, # The Pokemon's health
            status_condition: StatusCondition | None, # The Pokemon's status condition, if any (ex: Burned, Poisoned, Paralyzed, etc)
            confused: bool, # Whether the Pokemon is confused or not
            held_item: str, # The Pokemon's current held item
            move_set: list[BattleMove], # The Pokemon's move set in 'BattleMove' form
            stat_changes: OptionalStatTable | None # Any active stat changes applied to the Pokemon
    ):
        # Initialize fields
        self.health = health
        self.status_condition = status_condition
        self.confused = confused
        self.held_item = held_item
        self.move_set = move_set
        self.stat_changes = stat_changes

        # Reset volatile fields that are reset between battles
        # Confusion, move disabled-ness, stat changes
        def reset_volatile():
            self.confused = False
            for move in self.move_set:
                move.disabled = False
            self.stat_changes = None