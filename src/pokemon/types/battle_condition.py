from src.pokemon.types.stat_table import OptionalStatTable
from src.pokemon.types.status_condition import StatusCondition

class BattleMove:
    def __init__(
            self,
            name: str,
            pp: int,
            max_pp: int,
            disabled: bool
    ):
        self.name = name
        self.pp = pp
        self.max_pp = max_pp
        self.disabled = disabled

class BattleCondition:
    def __init__(
            self,
            health: int,
            status_condition: StatusCondition | None,
            confused: bool,
            held_item: str,
            move_set: list[BattleMove],
            stat_changes: OptionalStatTable | None
    ):
        self.health = health
        self.status_condition = status_condition
        self.confused = confused
        self.held_item = held_item
        self.move_set = move_set
        self.stat_changes = stat_changes

        def reset_volatile():
            self.confused = False
            for move in self.move_set:
                move.disabled = False
                move.pp = move.max_pp
            self.stat_changes = None