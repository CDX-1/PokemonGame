# Contains classes that contain metadata about a Pokemon's
# possible evolutions and how to evolve them.

# Imports

from __future__ import annotations # Allows a class to reference a type that is declared later

from typing import TypedDict, Any

# Define 'Evolution' class which is a dictionary with specific types (TypedDict)

class Evolution(TypedDict):
    name: str # The name of the evolution
    method: EvolutionMethod # The method used to evolve the Pokemon

# Define 'EvolutionMethod' class which is a dictionary with specific types (TypedDict)

class EvolutionMethod(TypedDict):
    name: str # The name of the evolution method
    parameter: Any # Any possible parameters needed for this method such as the level or held item