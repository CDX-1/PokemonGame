# This file represents a battle between two opposing sides
# and is the underlying/technical side of the battling
# mechanic

# Imports

from enum import Enum
from typing import Callable

import math
import random

from src.pokemon.pokemon import Pokemon
from src.pokemon.types.ball import Ball
from src.pokemon.types.catch_context import CatchContext
from src.pokemon.types.encounter_type import EncounterType
from src.pokemon.types.stat import Stat

# Define an enum for battle events
class BattleEvent(Enum):
    START_BATTLE = "start_battle"
    CATCH_START = "catch_start"
    CATCH_SHAKE = "catch_shake"
    CATCH_FAIL = "catch_fail"
    CATCH_SUCCESS = "catch_success"
    NEXT_TURN = "next_turn"
    END_BATTLE = "end_battle"
    CURRENT_POKEMON_UPDATE = "current_pokemon_update"

# Define the 'Battle' class
class Battle:
    # Class constructor method takes a list of Pokemon for the
    # player's team and a list of Pokemon for the opponents team
    # and an is_trainer flag
    def __init__(self, team: list[Pokemon], opponent_team: list[Pokemon], is_trainer: bool):
        # Ensure both sides have at least one Pokemon
        if not len(team) > 0 or not len(opponent_team) > 0:
            # Throw an error
            raise AttributeError('Each side must have at least one Pokemon')

        # Initialize fields
        self.team = team
        self.opponent_team = opponent_team
        self.is_trainer = is_trainer

        self.event_listeners: dict[BattleEvent, list[Callable[..., None]]] = {}

        # Initialize state fields
        self.current = team[0]
        self.current_opponent = opponent_team[0]
        self.turn = 0

    # Define a private function to call a BattleEvent
    def __call_event(self, event: BattleEvent, *args, **kwargs):
        # Ensure a list for this event type exists in listeners
        if not event in self.event_listeners:
            return # No listeners

        # Iterate all listeners for this event
        for listener in self.event_listeners[event]:
            # Call the listener callback
            listener(*args, **kwargs)

    # Define a function to add an event listener
    def listen(self, event: BattleEvent, listener: Callable[..., None]):
        # Ensure a list for this event type exists in listeners
        if not event in self.event_listeners:
            self.event_listeners[event] = []

        # Append this listener to the listeners for this event
        self.event_listeners[event].append(listener)

    # Define a function to start the battle
    def start_battle(self):
        # Call the start battle event
        self.__call_event(BattleEvent.START_BATTLE)
        # Send a message containing the current Pokemon
        self.__call_event(BattleEvent.CURRENT_POKEMON_UPDATE, self.current, self.current_opponent)

    # Define a function to handle catching the opposing Pokemon that
    # takes a Poke Ball
    # TODO Use Pokemon's actual health instead of turn counter once moves are implemented
    def catch(self, ball: Ball):
        import src.holder as holder

        # Check if this battle is a trainer battle
        if self.is_trainer:
            # Throw an error
            raise Exception("Cannot use the 'catch' method in a trainer battle")

        # This formula is derived from Bulbapedia
        # https://bulbapedia.bulbagarden.net/wiki/Catch_rate

        # Define variables for the formula
        max_health = self.current_opponent.get_stat(Stat.HP)
        current_health = self.current_opponent.get_stat(Stat.HP) / 2 # Presume half health TODO use actual health
        catch_rate = self.current_opponent.get_species().catch_rate
        ball_bonus = ball.value.handler(CatchContext(
            self.current,
            self.current_opponent,
            EncounterType.GRASS, # TODO Implement other encounter types
            self.turn
        ))
        status_bonus = 1 # TODO Implement status condition bonuses
        other_modifiers = 1

        # Calculate formula
        a = (((3 * max_health - 2 * current_health) * catch_rate * ball_bonus * status_bonus * other_modifiers) / (3 * max_health))

        # Initialize variables
        shakes = 0
        is_caught = False

        # Check if a is greater than or equal to 255
        if a >= 255:
            # Pokemon is automatically catch
            is_caught = True
            shakes = 4
        else:
            # Perform a 4-shake check to check if the Pokemon is caught
            b = 1048560 / math.sqrt(math.sqrt(16711680 / a))  # Derived constant, formula from Bulbapedia
            for i in range(4): # Check for a passed shake 4 times
                if random.randint(0, 65535) >= b:
                    # The Pokemon broke free
                    is_caught = False
                    break
                # Increment shake counter
                shakes += 1
            # All 4 shakes passed, catch is successful
            is_caught = True
            shakes = 4

        # Send a catch start event
        self.__call_event(BattleEvent.CATCH_START, ball)

        # Send a catch shake event for each shake
        for i in range(shakes - 1):
            holder.root.after((i * 1000) + 1000, lambda: self.__call_event(BattleEvent.CATCH_SHAKE))

        # Define a callback to run after all the shakes have completed
        def callback():
            # Check if the catch was successful and call respective event
            if is_caught:
                self.__call_event(BattleEvent.CATCH_SUCCESS)
                self.end_battle()
            else:
                self.__call_event(BattleEvent.CATCH_FAIL)
                self.next_turn()

        # Queue the callback
        holder.root.after(shakes * 1000, callback)

    # Define a function to increment the turn counter
    def next_turn(self):
        self.turn += 1
        # Call the next turn event
        self.__call_event(BattleEvent.NEXT_TURN)

    # Define a function to end the battle
    def end_battle(self):
        # Call the end battle event
        self.__call_event(BattleEvent.END_BATTLE)