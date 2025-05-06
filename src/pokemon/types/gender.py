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