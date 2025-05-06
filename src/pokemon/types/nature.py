# This file defines an enum for every possible nature a Pokemon can have. A nature
# influences two of a Pokemon's stats. It increases one by 10% and decreases another
# by 10%. Some natures increase and decrease the same stat, making them effectively
# neutral.

# Imports

from enum import Enum

from src.pokemon.types.stat import Stat

# Define a class called 'Nature' that extends 'Enum'

class Nature(Enum):
    # Define natures using a tuple where the first element is the increased
    # stat and the second element is the decreased stat
    ADAMANT = (Stat.ATTACK, Stat.SPECIAL_ATTACK)
    BASHFUL = (Stat.SPECIAL_ATTACK, Stat.SPECIAL_ATTACK)        # NEUTRAL
    BOLD = (Stat.DEFENSE, Stat.ATTACK)
    BRAVE = (Stat.ATTACK, Stat.SPEED)
    CALM = (Stat.SPECIAL_DEFENSE, Stat.ATTACK)
    CAREFUL = (Stat.SPECIAL_DEFENSE, Stat.SPECIAL_ATTACK)
    DOCILE = (Stat.DEFENSE, Stat.DEFENSE)                       # NEUTRAL
    GENTLE = (Stat.SPECIAL_DEFENSE, Stat.DEFENSE)
    HARDY = (Stat.ATTACK, Stat.ATTACK)                          # NEUTRAL
    HASTY = (Stat.SPEED, Stat.DEFENSE)
    IMPISH = (Stat.DEFENSE, Stat.SPECIAL_ATTACK)
    JOLLY = (Stat.SPEED, Stat.SPECIAL_ATTACK)
    LAX = (Stat.DEFENSE, Stat.SPECIAL_DEFENSE)
    LONELY = (Stat.ATTACK, Stat.DEFENSE)
    MILD = (Stat.SPECIAL_ATTACK, Stat.DEFENSE)
    MODEST = (Stat.SPECIAL_ATTACK, Stat.ATTACK)
    NAIVE = (Stat.SPEED, Stat.SPECIAL_DEFENSE)
    NAUGHTY = (Stat.ATTACK, Stat.SPECIAL_DEFENSE)
    QUIET = (Stat.SPECIAL_ATTACK, Stat.SPEED)
    QUIRKY = (Stat.SPECIAL_DEFENSE, Stat.SPECIAL_DEFENSE)       # NEUTRAL
    RASH = (Stat.SPECIAL_ATTACK, Stat.SPECIAL_DEFENSE)
    RELAXED = (Stat.DEFENSE, Stat.SPEED)
    SASSY = (Stat.SPECIAL_DEFENSE, Stat.SPEED)
    SERIOUS = (Stat.SPEED, Stat.SPEED)                          # NEUTRAL
    TIMID = (Stat.SPEED, Stat.ATTACK)