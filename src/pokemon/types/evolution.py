from __future__ import annotations

from typing import TypedDict, Any


class Evolution(TypedDict):
    name: str
    method: EvolutionMethod

class EvolutionMethod(TypedDict):
    name: str
    parameter: Any