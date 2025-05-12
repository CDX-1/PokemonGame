# This file contains an enum that represents possible damage classes a
# move can fall into. (ex: Physical, Special, Status). Different damage
# classes use a different defense stat to calculate final damage.

# Imports

from enum import Enum

# Define 'DamageClass' enum by creating a class that extends 'Enum'

class DamageClass(Enum):
    # Define enumerators using string literal values
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

    # Define a format function that formats the damage class for GUIs
    def format(self):
        if self.value == "physical":
            return "PHYS"
        elif self.value == "special":
            return "SPEC"
        elif self.value == "status":
            return "STAT"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Iterate all enumerations
        for entry in DamageClass:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value.lower() or entry.value.lower() == value.lower():
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid damage class: {value}")