from typing import cast

import requests

from src.pokemon.species import Species, Abilities, GenderRatio, SpriteTable, SpritePair
from src.pokemon.types.egg_groups import EggGroup
from src.pokemon.types.evolution import Evolution, EvolutionMethod
from src.pokemon.types.growth_rate import GrowthRate
from src.pokemon.types.stat_table import OptionalStatTable, StatTable

kanto_dex = requests.get("https://pokeapi.co/api/v2/pokedex/2").json()
for pokemon_summary in kanto_dex["pokemon_entries"]:
    species_summary = pokemon_summary["pokemon_species"]
    name = species_summary["name"]

    species_endpoint = species_summary["url"]
    species_data = requests.get(species_endpoint).json()

    dex_id = list(filter(lambda entry: entry["pokedex"]["name"] == "national", species_data["pokedex_numbers"]))[0]["entry_number"]

    pokemon_data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{dex_id}").json()

    clean_name = str.join("_", str.split(name, " ")).lower()
    genus = list(filter(lambda entry: entry["language"]["name"] == "en", species_data["genera"]))[0]["genus"]
    types = list(map(lambda entry: entry["type"]["name"], pokemon_data["types"]))

    raw_regular_abilities = list(filter(lambda entry: entry["is_hidden"] == False, pokemon_data["abilities"]))
    raw_hidden_abilities = list(filter(lambda entry: entry["is_hidden"] == True, pokemon_data["abilities"]))

    regular_abilities = list(map(lambda entry: entry["ability"]["name"], raw_regular_abilities))
    hidden_abilities = list(map(lambda entry: entry["ability"]["name"], raw_hidden_abilities))

    evolutions = []
    evolution_chain = requests.get(species_data["evolution_chain"]["url"]).json()
    if len(evolution_chain["chain"]["evolves_to"]) > 0:
        target = evolution_chain["species"]["name"]
        first = evolution_chain["chain"]["evolves_to"]

        while target != name:
            target = first["species"]["name"]
            first = first["evolves_to"]

        acceptable_methods = list(filter(lambda entry: entry["location"] is None and entry["trigger"]["name"] in ["use-item", "level-up", "trade"], first["evolution_details"]))
        if len(acceptable_methods) == 0:
            print(f"Failed to find acceptable evolution method for: {clean_name} [{name}]")
        else:
            evolution_method = None
            method = acceptable_methods[0]
            trigger = method["trigger"]["name"]
            if trigger is "level-up":
                evolution_method = EvolutionMethod(
                    name="levelup",
                    parameter=method["min_level"]
                )
            elif trigger is "use-item":
                evolution_method = EvolutionMethod(
                    name="use_item",
                    parameter=str.join("_", str.split("-", method["item"]["name"])).lower()
                )
            elif trigger is "trade":
                evolution_method = EvolutionMethod(
                    name="trade",
                    parameter=None
                )

            evolutions.append(
                Evolution(
                    name=target,
                    method=evolution_method
                )
            )

    base_stats = {}
    ev_yield = {}

    for stat in pokemon_data["stats"]:
        stat_name = stat["stat"]["name"].replace("-", "_")
        base_stats[stat_name] = stat["base_stat"]
        if stat["effort"] > 0:
            ev_yield[stat_name] = stat["effort"]

    gender_ratio = None
    female_chance = species_data["gender_rate"] / 8
    if not female_chance < 0:
        gender_ratio = GenderRatio(
            male=1 - female_chance,
            female=female_chance
        )

    species = Species(
        dex_id,
        clean_name,
        name,
        genus,
        types,
        Abilities(
            regular=regular_abilities,
            hidden=hidden_abilities
        ),
        evolutions,
        pokemon_data["height"] / 10,
        pokemon_data["weight"] / 10,
        cast(OptionalStatTable, ev_yield),
        species_data["capture_rate"],
        species_data["base_happiness"],
        pokemon_data["base_experience"],
        GrowthRate.of(species_data["growth_rate"]["name"].replace("-", "_")),
        list(map(lambda entry: EggGroup.of(entry["name"]), species_data["egg_groups"])),
        species_data["hatch_counter"],
        gender_ratio,
        cast(StatTable, base_stats),
        [],
        SpriteTable(
            regular=SpritePair(
                front="",
                back=""
            ),
            shiny=SpritePair(
                front="",
                back=""
            )
        )
    )