# This file acts as a one-time script instead of a module of the
# main program. This script is used to download Pokemon data and
# simplify it into a single distributable JSON file (called a 'pack').
# This script is specifically for generating a generation 1 pack and
# will only contain the first 151 original Pokemon.

# For reference, this API is used to obtain all Pokemon data: https://pokeapi.co/

# Imports

from collections.abc import Callable
from typing import cast, Any, TypeVar

import src.utils.requests as requests
import json

from src.generator.tools.purifier import purify_obj
from src.pokemon.species import Species, Abilities, GenderRatio, SpriteTable, SpritePair
from src.pokemon.types.damage_class import DamageClass
from src.pokemon.types.egg_groups import EggGroup
from src.pokemon.types.evolution import Evolution, EvolutionMethod
from src.pokemon.types.growth_rate import GrowthRate
from src.pokemon.types.learnable_move import LearnableMove
from src.pokemon.move import Move
from src.pokemon.types.move_ailment import MoveAilment
from src.pokemon.types.move_category import MoveCategory
from src.pokemon.types.move_target import MoveTarget
from src.pokemon.types.stat_table import OptionalStatTable, StatTable, BattleStatTable

# Define all_species, all_moves, and move_names lists in order to reduce
# amount of HTTP requests later in the code by caching this information

all_species = []
all_moves = []
move_names = []

# Inform user that the download process is beginning

print("Downloading Pokemon...")

# Retrieve a JSON formatted object containing a list of the original 151 Pokemon

kanto_dex = requests.get("https://pokeapi.co/api/v2/pokedex/2").json()

# Iterate each Pokemon's 'summary' in the 'pokemon_entries' list
for pokemon_summary in kanto_dex["pokemon_entries"]:
    # Retrieve 'species' summary
    species_summary = pokemon_summary["pokemon_species"]
    # Retrieve species name
    name = species_summary["name"]

    # Inform user that data for the specific species is being downloaded
    print(f"Downloading data for {name}...")

    # Obtain URL to get full species data
    species_endpoint = species_summary["url"]
    # Perform HTTP request to retrieve full species data from URL
    species_data = requests.get(species_endpoint).json()

    # Filter the species pokedex numbers to find the Pokemon's national number AKA it's globally unique ID number
    dex_id = list(filter(lambda entry: entry["pokedex"]["name"] == "national", species_data["pokedex_numbers"]))[0]["entry_number"]

    # Perform HTTP request using globally unique ID number to retrieve Pokemon data
    pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{dex_id}").json()

    # Clean the name of the Pokemon as its species name usually contains separators such as underscores
    clean_name = str.join("_", str.split(name, " ")).lower()
    # Determine the English genus/brief description of the species by filtering the genera
    genus = list(filter(lambda entry: entry["language"]["name"] == "en", species_data["genera"]))[0]["genus"]
    # Map the Pokemon's types to a string list as the type list contains nested objects by default
    types = list(map(lambda entry: entry["type"]["name"], pokemon_data["types"]))

    # Filter the Pokemon's abilities by its non-hidden ability flag and put into a list
    raw_regular_abilities = list(filter(lambda entry: entry["is_hidden"] == False, pokemon_data["abilities"]))
    # Filter the Pokemon's abilities by its hidden ability flag and put into a list
    raw_hidden_abilities = list(filter(lambda entry: entry["is_hidden"] == True, pokemon_data["abilities"]))

    # Map the raw regular abilities list which contains objects into a string list
    regular_abilities = list(map(lambda entry: entry["ability"]["name"].replace("-", "_"), raw_regular_abilities))
    # Map the raw hidden abilities list which contains objects into a string list
    hidden_abilities = list(map(lambda entry: entry["ability"]["name"].replace("-", "_"), raw_hidden_abilities))

    # Initialize an empty list to contain all the Pokemon's evolutions
    evolutions = []
    # Perform an HTTP request to the evolution chain URL of hte species in order to find all (pre)evolutions
    evolution_chain = requests.get(species_data["evolution_chain"]["url"]).json()

    # Define a function that will be used to recursively search a list of objects for this Pokemon's name
    def find_evolution_node(chain, name):
        # Check if the current species matches the target species
        if chain["species"]["name"] == name:
            return chain
        # Otherwise iterate all evolutions of the current species
        for evo in chain["evolves_to"]:
            # Check if it matches the name of the target species through recursion
            result = find_evolution_node(evo, name)
            # Return the result if the name matches, effectively breaking the nested recursion
            if result is not None:
                return result
        # Return none if nodes are found (should not happen)
        return None

    # Find the Pokemon's respective evolution node
    node = find_evolution_node(evolution_chain["chain"], name)
    # Check if the Pokemon has any evolutions
    if node and len(node["evolves_to"]) > 0:
        # Iterate each of the Pokemon's evolutions
        for evo in node["evolves_to"]:
            # Filter for acceptable evolution methods: no location requirement and specific triggers,
            # accounts for Pokemon that have multiply evolution methods
            acceptable_methods = [
                method for method in evo["evolution_details"]
                if method["location"] is None and method["trigger"]["name"] in ["use-item", "level-up", "trade"]
            ]
            if acceptable_methods:
                # Retrieve the method of evolution
                method = acceptable_methods[0]
                # Retrieve the evolution's trigger
                trigger = method["trigger"]["name"]

                # Handle different evolution triggers
                if trigger == "level-up" and method["min_level"] is not None:
                    # Create an evolution method specification for level-up evolutions
                    evolution_method = EvolutionMethod(name="levelup", parameter=method["min_level"])
                elif trigger == "use-item":
                    # Create an evolution method specification for item evolutions
                    item_name = method["item"]["name"].replace("-", "_").lower()
                    evolution_method = EvolutionMethod(name="use_item", parameter=item_name)
                elif trigger == "trade":
                    # Create an evolution method specification for trade evolutions
                    evolution_method = EvolutionMethod(name="trade", parameter=None)
                else:
                    continue # Skip if method doesn't match expected criteria (should not happen)

                # Add the evolution to the list of evolutions
                evolutions.append(Evolution(name=evo["species"]["name"], method=evolution_method))
            else:
                # Inform user that an acceptable evolution method was not found
                print(f"Failed to find acceptable evolution method for: {name} to {evo['species']['name']}")

    # Initialize a dictionary to store the Pokemon's base stats
    base_stats = {}
    # Initialize a directory to store the Pokemon's effort value (EV) yield
    ev_yield = {}

    # Iterate the Pokemon's stats
    for stat in pokemon_data["stats"]:
        # Parse the actual name of the stat
        stat_name = stat["stat"]["name"].replace("-", "_")
        # Insert the base stat into the base stat dictionary
        base_stats[stat_name] = stat["base_stat"]
        # Check if this stat rewards any effort values
        if stat["effort"] > 0:
            # Add this stat to the effort values dictionary
            ev_yield[stat_name] = stat["effort"]

    # Initialize the gender ratio as none
    gender_ratio = None
    # Calculate the chance of this Pokemon being female by using its gender rate (in percent form)
    female_chance = species_data["gender_rate"] / 8
    # If the Pokemon is not genderless (chance of being female would be negative)
    if not female_chance < 0:
        # Specify the gender ratio and calculate the male chance by subtracting 1 by the female chance
        gender_ratio = GenderRatio(
            male=1 - female_chance,
            female=female_chance
        )

    # Initialize an empty list of the moves the Pokemon can learn
    moves = []
    # Iterate each move the Pokemon can learn according to the API
    for move in pokemon_data["moves"]:
        # Retrieve the move's name
        move_name = move["move"]["name"]
        # Initialize an empty instance of a 'LearnableMove' which contains data
        # about how the move can be learnt by this Pokemon
        learnable_move = LearnableMove(move_name.replace("-", "_"), None, False, False)
        # Iterate each method this Pokemon has for learning this move
        for method in move["version_group_details"]:
            # Retrieve the method name
            method_name = method["move_learn_method"]["name"]
            # Handle different learning methods
            if method_name == "level-up":
                # Specify the level this move can be learnt at
                learnable_move.level = method["level_learned_at"]
            elif method_name == "machine":
                # Mark this as a machine move (can be taught to the Pokemon using a Technical Machine (TM))
                learnable_move.machine = True
            elif method_name == "tutor":
                # Mark this move as a tutorable move (can be taught to the Pokemon using a move tutor)
                learnable_move.tutor = True
        # Check if the move has any valid learning conditions
        if learnable_move.level is not None or learnable_move.machine != False or learnable_move.tutor != False:
            # Add the move to the list of moves this Pokemon can learn
            moves.append(learnable_move)
            # Check if this move was added to the global move name list
            if move_name not in move_names:
                # Add if not added already, prevents repetitive entries
                move_names.append(move_name)

    # Initialize the 'Species' object which contains all data about the Pokemon
    species = Species(
        dex_id, # Global unique ID
        clean_name, # A clean displayable name
        name, # An identifier name (might contain underscores)
        # Filters the Pokemon's flavours (descriptive texts) by the English version
        # Retrieves the first flavour that is written in English, replace all 'e's that
        # have an accent with a standard 'e' to prevent certain systems from failing to
        # render the different type of 'e' character
        list(filter(lambda entry: entry["language"]["name"] == "en", species_data["flavor_text_entries"]))[0]["flavor_text"].replace("\u00e9", "e"),
        genus.replace("\u00e9", "e"), # The genus (brief description), replace accented 'e' with a plain 'e'
        types, # The pokemon's type(s) (maximum of 2)
        Abilities(
            regular=regular_abilities, # The Pokemon's regular abilities
            hidden=hidden_abilities # The Pokemon's hidden abilities
        ),
        evolutions, # The Pokemon's possible evolutions
        pokemon_data["height"] / 10, # The Pokemon's height, divided by ten to convert (decimeters -> meters)
        pokemon_data["weight"] / 10, # The Pokemon's weight, divided by ten to convert (hectograms -> kilograms)
        cast(OptionalStatTable, ev_yield), # Cast the original effort value dictionary to an 'OptionalStatTable'
        species_data["capture_rate"], # The catch rate, retrieved from the API
        species_data["base_happiness"], # The base happiness, retrieved from the API
        pokemon_data["base_experience"], # The base experience, retrieved from the API
        GrowthRate.of(species_data["growth_rate"]["name"].replace("-", "_")), # The Pokemon's growth rate, converted from kebab-case to snake_case
        list(map(lambda entry: EggGroup.of(entry["name"]), species_data["egg_groups"])), # The Pokemon's egg groups mapped to a string list
        species_data["hatch_counter"], # The egg cycles (AKA hatch counter) needed to hatch the Pokemon's egg
        gender_ratio, # The gender ratio
        cast(StatTable, base_stats), # Cast the original base stats dictionary to a StatTable (no optional fields)
        moves, # The learnable moves
        # An object that provides a list of links to download the Pokemon's image assets from
        SpriteTable(
            regular=SpritePair(
                front=f"https://img.pokemondb.net/sprites/emerald/normal/{name}.png", # Front view, regular variation
                back=f"https://img.pokemondb.net/sprites/emerald/back-normal/{name}.png" # Back view, regular variation
            ),
            shiny=SpritePair(
                front=f"https://img.pokemondb.net/sprites/emerald/shiny/{name}.png", # Front view, shiny variation
                back=f"https://img.pokemondb.net/sprites/emerald/back-shiny/{name}.png" # Back view, shiny variation
            )
        )
    )

    # Add the Pokemon species to the list of all species
    all_species.append(species)
    # Inform user that the Pokemon's data has been successfully downloaded
    print(f"Done downloading {name}")

# After all Pokemon's data have been downloaded, inform the user and list the amount of successful downloads
print(f"Done downloaded {len(all_species)} Pokemon")

# Inform user that the downloading of moves will start now
print("Downloading moves...")

# Initialize the type generic 'T'
T = TypeVar('T')

# Define a function that will check a move's meta, process it, and return a specified
# key in the meta or a default value of 'otherwise', uses the 'T' type generic to appease
# Python's type hints, this means that the value of the key must be the same type as the
# 'otherwise' argment
def check_meta_or_else_complex(obj: Any, key: str, processor: Callable[[Any], T], otherwise: T) -> T:
    if obj["meta"] is not None:
        return processor(obj["meta"][key]["name"])
    else:
        return otherwise

# Define a function that will check a move's meta to see if it exists, if not, it will return
# the 'otherwise' argument which is of the same type as the value of the 'key' argument assuming
# it is not 'None'
def check_meta_or_else(obj: Any, key: str, otherwise: T) -> T:
    if obj["meta"] is not None:
        return obj["meta"][key]
    else:
        return otherwise

# Define a function that will be used to check the move's meta and return a percent value
# or 'None' if the percent value is not specified for this move, this will only be the case
# for percents hence why the name of the function is so specific
def check_percent_meta_or_else(obj: Any, key: str) -> float | None:
    if obj["meta"] is not None:
        if key in obj["meta"]:
            return obj["meta"][key]
    return None

# Iterate every move name that was specified in the learnable moves
# This prevents moves that can't be learnt from being downloaded
for move_name in move_names:
    # Inform user that the data for the move is being downloaded
    print(f"Downloading move {move_name}...")
    # Retrieve the move's raw data from the API
    data = requests.get(f"https://pokeapi.co/api/v2/move/{move_name.replace('_', '-')}").json()
    # Retrieve the move's metadata
    meta = data["meta"]
    # Initialize the 'Move' object that contains all the move's necessary data
    move = Move(
        data["id"], # The move's unique numerical ID
        data["name"].replace("-", "_"), # THe move's name converted from kebab-case to snake_case
        # Filters the move's flavours (descriptive texts) by the English version
        # Retrieves the first flavour that is written in English, replace all 'e's that
        # have an accent with a standard 'e' to prevent certain systems from failing to
        # render the different type of 'e' character
        list(filter(lambda entry: entry["language"]["name"] == "en", data["flavor_text_entries"]))[0]["flavor_text"].replace("\u00e9", "e"),
        data["type"]["name"], # The move's type (only one)
        data["accuracy"], # The accuracy of the move
        data["effect_chance"], # The chance that this move will trigger its effect
        data["pp"], # The max power points of this move (AKA amount of usages before the Pokemon must be healed)
        data["priority"], # The move's priority (ranging from -8 to 8)
        data["power"], # The move's base power
        DamageClass.of(data["damage_class"]["name"]), # The damage class of the move (PHYSICAL, SPECIAL, STATUS)
        # Cast a mapped dictionary of strings containing any stat changes this move may make to a 'BattleStatTable'
        # which is an extension of the 'StatTable' but contains volatile stats such as accuracy and evasion
        cast(BattleStatTable, dict(map(lambda entry: (entry["stat"]["name"].replace("-", "_"), entry["change"]), data["stat_changes"]))),
        MoveTarget.of(data["target"]["name"]), # The move's targets (ex: opponent, self, field(s))
        check_meta_or_else_complex(data, "ailment", lambda key: MoveAilment.of(key), MoveAilment.NONE), # The ailment the move may inflict, if any
        check_meta_or_else_complex(data, "category", lambda key: MoveCategory.of(key), MoveCategory.UNKNOWN), # The category of the move
        check_meta_or_else(data, "min_hits", None), # The minimum amount of hits this move can do (if it is a multi-hit move)
        check_meta_or_else(data, "max_hits", None), # The maximum amount of hits this move can do (if it is a multi-hit move)
        check_meta_or_else(data, "max_turns", None), # The maximum amount of turns the effects of this move can last (if its effect persists)
        check_percent_meta_or_else(data, "drain"), # The percent of the target's health to drain
        check_percent_meta_or_else(data, "healing"), # The percent of the total damage dealt by this move to heal the user
        check_percent_meta_or_else(data, "crit_chance"), # The chance that this move lands a critical hit (1.5x damage)
        check_percent_meta_or_else(data, "ailment_chance"), # The chance that this move inflicts its ailment (if it has one)
        check_percent_meta_or_else(data, "flinch_chance"), # The chance that this move will cause the target to flinch
        check_percent_meta_or_else(data, "stat_chance") # The chance that this move will perform stat changes
    )

    # Add this move to the list of all moves
    all_moves.append(move)
    # Inform the user that the move has successfully been downloaded
    print(f"Downloaded move {move_name}")

# Inform the user how many moves have been successfully downloaded and that the download is complete
print(f"Done downloading {len(all_moves)} moves")

# Open the 'packs/gen-1.json' file in 'write' mode as 'file'
with open("packs/gen-1.json", "w") as file:
    # Dump a purified copy of the 'species' and 'moves' lists to the file
    # The specified separators is a micro-optimization done to reduce the
    # size of the resulting JSON file by reducing unnecessary whitespace
    json.dump(purify_obj({
        "species": list(map(lambda entry: entry.__dict__, all_species)),
        "moves": list(map(lambda entry: entry.__dict__, all_moves))
    }), file, separators=(",", ":"))

# Inform the user that the script has finished and the pack has been generated
print("Done generating pack!")