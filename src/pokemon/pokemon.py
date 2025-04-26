from src.pokemon.species import Species
from src.pokemon.types.battle_condition import BattleCondition
from src.pokemon.types.capture_data import CaptureData
from src.pokemon.types.gender import Gender
from src.pokemon.types.nature import Nature
from src.pokemon.types.stat_table import StatTable

class Pokemon:
    def __init__(
            self,
            nickname: str,
            egg: bool,
            shiny: bool,
            species: Species,
            ability: str,
            gender: Gender,
            nature: Nature,
            ivs: StatTable,
            evs: StatTable,
            level: int,
            experience: int,
            friendship: int,
            condition: BattleCondition,
            capture_data: CaptureData
    ):
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