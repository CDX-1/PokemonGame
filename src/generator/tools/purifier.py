# This file is used to convert a Python object into serializable data structures
# such as dicts and lists. The primary purpose of this utility module is to purify
# objects so that they can be written to a JSON file

# Imports

from enum import Enum
from typing import Any, Iterable, Mapping

# Define purify function which takes an object and returns a data structure (dict, list), primitive string, or none

def purify_obj(obj: Any) -> list[Any] | str | None | dict[str, str] | Any:
    # Check if the object is already pure, if so then return object as is
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # Check if the object is an enum, if so, return the enum's name
    if isinstance(obj, Enum):
        return obj.name

    # Check if the object is a mappable structure (such as a dictionary)
    # and purify each sub-element in the structure recursively
    if isinstance(obj, Mapping):
        return { purify_obj(k): purify_obj(v) for k, v in obj.items() }

    # Check if the object is an iterable such as a list and purify
    # each sub-element of the list recursively
    if isinstance(obj, Iterable):
        return [ purify_obj(item) for item in obj ]

    # Check if the object is a class object, if so, obtain the fields
    # of the object and purify them recursively
    if hasattr(obj, '__dict__'):
        return purify_obj(vars(obj))

    # Final catch-all measure, if the object cannot be serialized in
    # any other way, then rely on Python's native serialization through
    # the 'str' function
    return str(obj)