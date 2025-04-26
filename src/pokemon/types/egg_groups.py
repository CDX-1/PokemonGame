from enum import Enum

class EggGroup(Enum):
    MONSTER = "monster",
    FAIRY = "fairy"
    HUMAN_IKE = "humanlike"
    FIELD = "field"
    FLYING = "flying"
    DRAGON = "dragon"
    BUG = "bug"
    WATER_1 = "water_1"
    WATER_2 = "water_2"
    WATER_3 = "water_3"
    GRASS = "grass"
    AMORPHOUS = "amorphous"
    MINERAL = "mineral"

    @staticmethod
    def of(value: str):
        if value == "humanshape":
            value = "humanlike"
        elif "water" in value:
            value = "water_" + value[-1]

        for group in EggGroup:
            if group.name.lower() == value.lower() or group.value == value.lower():
                return group
        raise KeyError(f"Unknown egg group: {value}")