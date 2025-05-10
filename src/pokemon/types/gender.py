# This class contains an enum to represent possible genders of a
# Pokemon which are male, female, and genderless.

# Imports

from enum import Enum

# Define 'Gender' enum by creating a class that extends 'Enum'

class Gender(Enum):
    # Define enumerations using string literal values
    MALE = "male",
    FEMALE = "female"
    GENDERLESS = "genderless"

    # Define a static method to access any enumeration object using a string literal
    @staticmethod
    def of(value: str):
        # Iterate all enumerations
        for entry in Gender:
            # Check if current enumeration's name or value matches the 'value' argument
            if entry.name.lower() == value.lower() or entry.value == value.lower():
                # Return matching enumeration
                return entry
        # Raise a KeyError to indicate invalid 'value' argument
        raise KeyError(f"Invalid gender: {value}")