from __future__ import annotations

from typing import TypedDict

from src.pokemon.types.egg_groups import EggGroup
from src.pokemon.types.evolution import Evolution
from src.pokemon.types.growth_rate import GrowthRate
from src.pokemon.types.stat_table import OptionalStatTable, StatTable


class Abilities(TypedDict):
    regular: list[str]
    hidden: list[str]

class GenderRatio(TypedDict):
    male: float
    female: float

class MoveTable(TypedDict):
    level_up: list[LeveledMoveSummary]
    egg_moves: list[MoveSummary]
    tms: list[MoveSummary]

class MoveSummary(TypedDict):
    id: str

class LeveledMoveSummary(TypedDict):
    id: str
    level: int

class SpriteTable(TypedDict):
    regular: SpritePair
    shiny: SpritePair

class SpritePair(TypedDict):
    front: str
    back: str

class Species:
    def __init__(
            self,
            dex_id: int,
            id: str,
            name: str,
            genus: str,
            types: list[str],
            abilities: Abilities,
            evolutions: list[Evolution],
            height: float,
            weight: float,
            ev_yield: OptionalStatTable,
            catch_rate: int,
            base_friendship: int,
            base_exp: int,
            growth_rate: GrowthRate,
            egg_groups: list[EggGroup],
            egg_cycles: int,
            gender_ratio: GenderRatio | None,
            base_stats: StatTable,
            moves: MoveTable,
            sprites: SpriteTable
    ):
        self.dex_id = dex_id
        self.id = id
        self.name = name
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
