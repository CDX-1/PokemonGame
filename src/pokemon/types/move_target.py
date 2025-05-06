# This file defines an enum that represents the different targets
# a move can have such as the user themselves, the opposing target,
# or an entire field for moves such as spike which inflict an effect
# on the field itself.

# Imports

from enum import Enum

# Define 'MoveTarget' enum by creating a class that extends 'Enum'

class MoveTarget(Enum):
    # Define enumerations using string literal values
    COUNTER = "counter"
    YOUR_SIDE = "your_side"
    OTHER_SIDE = "other_side"
    ALL_SIDES = "all_sides"
    OTHER = "other"
    SELF = "self"
    ALL = "all"
    UNIMPLEMENTED = "unimplemented"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Convert value to lowercase
        value_lower = value.lower()
        # Iterate all enumerations
        for entry in MoveTarget:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value_lower or entry.value == value_lower:
                # Return matching enumeration
                return entry
        # Define a dictionary of target mappings, some targets that exist in actual Pokemon games
        # are not fully implemented and are instead remapped to other targets
        _target_mapping = {
            "specific-move": MoveTarget.COUNTER,
            "selected-pokemon-me-first": MoveTarget.UNIMPLEMENTED,
            "ally": MoveTarget.UNIMPLEMENTED,
            "users-field": MoveTarget.YOUR_SIDE,
            "user-or-ally": MoveTarget.SELF,
            "opponents-field": MoveTarget.OTHER_SIDE,
            "user": MoveTarget.SELF,
            "random-opponent": MoveTarget.OTHER,
            "all-other-pokemon": MoveTarget.OTHER,
            "selected-pokemon": MoveTarget.OTHER,
            "all-opponents": MoveTarget.OTHER,
            "entire-field": MoveTarget.ALL_SIDES,
            "user-and-allies": MoveTarget.SELF,
            "all-pokemon": MoveTarget.ALL,
            "all-allies": MoveTarget.UNIMPLEMENTED,
            "fainting-pokemon": MoveTarget.UNIMPLEMENTED
        }
        # Check if the value is in the mapping dictionary
        if value_lower in _target_mapping:
            # Return matching target
            return _target_mapping[value_lower]
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid move target: {value}")