from enum import Enum

class StatusCondition(Enum):
    PARALYZED = "paralyzed"
    BURNED = "burned"
    POISONED = "poisoned"
    BADLY_POISONED = "bad_poisoned"
    SLEEPING = "sleeping"
    FROZEN = "frozen"