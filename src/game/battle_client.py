# This file defines the 'BattleClient' a special class that communicates with a
# battle simulation server to handle Pokemon battle processing and simulation

# Imports

import json
import math
import random
import socket
import threading
from enum import Enum
from typing import Any, Callable

from src import holder
from src.pokemon.pokemon import Pokemon
from src.pokemon.types.ball import Ball
from src.pokemon.types.catch_context import CatchContext
from src.pokemon.types.encounter_type import EncounterType

# Define constants for battle simulation server
host = "129.153.58.254"
port = 3000

# Define an enum to separate the player and an AI opponent
class Battler(Enum):
    PLAYER = "1"
    AI = "2"

# Define an enum to categorize battle events
class BattleEvent(Enum):
    STARTED = "started" # Simulation has started
    MOVE = "move" # A move was used
    STAT_CHANGE = "stat_change" # A Pokemon has had their stats changed
    CATCH = "catch_success" # A successful or unsuccessful catch
    TURN_CHANGE = "turn_change" # The turn counter has updated
    PP_UPDATE = "pp_update" # Move PP has been updated
    CURRENT_POKEMON_UPDATE = "current_pokemon_update" # A Pokemon on the field has been updated
    HEALTH_UPDATE = "health_update" # A Pokemon's health has been updated
    CRITICAL_HIT = "critical_hit" # A move landed a critical hit
    SUPER_EFFECTIVE = "super_effective" # A move was super effective
    RESISTED = "resisted" # A move was resisted
    IMMUNE = "immune" # A move did no damage
    FAINTED = "fainted" # A Pokemon has fainted
    FAILED = "failed" # A move has failed
    BLOCKED = "blocked" # A move has been blocked
    HEAL = "heal" # A Pokemon has had itş health restored
    STATUS_INFLICTED = "status_inflicted" # A Pokemon was inflicted with a status condition
    STATUS_CURED = "status_cured" # A Pokemon has had its status condition cured
    TEAM_STATUS_CURED = "team_status_cured" # The entire team had their status conditions cured
    STAT_SWAPPED = "stat_swapped" # The stat changes were swapped between a target and another Pokemon
    STAT_CHANGES_INVERTED = "stat_changes_inverted" # The stat changes of the Pokemon were inverted
    STAT_CHANGES_CLEARED = "stat_changes_cleared" # All the stat changes have been cleared
    ALL_STAT_CHANGES_CLEARED = "all_stat_changes_cleared" # All stat changes of all Pokemon on both sides have been cleared
    CLEAR_POSITIVE_STAT_CHANGES = "clear_positive_stat_changes" # All positive stat changes were cleared from target
    CLEAR_NEGATIVE_STAT_CHANGES = "clear_negative_stat_changes" # All negative stat changes were cleared from target
    COPY_STAT_CHANGES = "copy_stat_changes" # All stat changes were copied by target
    WEATHER = "weather" # The weather has changed
    FIELD_START = "field_start" # A condition has been added to the field
    FIELD_END = "field_end" # A condition on the field has ended
    SIDE_START = "side_start" # A condition has started on one side of the field
    SIDE_END = "side_end" # A condition has ended on one side of the field
    SWAP_SIDE_CONDITIONS = "swap_side_conditions" # The side conditions have been swapped
    VOLATILE_STATUS_STARTED = "volatile_status_started" # A volatile status condition (ex: Taunt) has started
    VOLATILE_STATUS_ENDED = "volatile_status_ended" # A volatile status condition (ex: Taunt) has ended
    ABILITY_CHANGED = "ability_changed" # A Pokemon's ability has changed
    ABILITY_ACTIVATED = "ability_activated" # A Pokemon's ability has been activated
    ABILITY_ENDED = "ability_ended" # A Pokemon's ability has been suppressed
    TRANSFORM = "transform" # A Pokemon has transformed into another Pokemon
    PREPARE_AGAINST_UNKNOWN = "prepare_against_unknown" # A Pokemon is preparing to use a move on an unknown target
    PREPARE_AGAINST_KNOWN = "prepare_against_known" # A Pokemon is preparing to use a move on a known target
    NOTHING = "nothing" # A move has done nothing
    MUST_RECHARGE = "must_recharge" # A Pokemon must recharge after using a move
    MOVE_MULTI_HIT = "move_multi_hit" # A move has hit its target an X amount of times
    SINGLE_MOVE = "single_move" # A Pokemon has used a move which has an effect that lasts for the duration of the move
    SINGLE_TURN = "single_turn" # A Pokemon has used a move which has an effect that lasts for the duration of the turn
    END = "end" # The battle has ended

    LOG = "log" # A message was sent or received

# Define the 'BattleClient' class
class BattleClient:
    # Class constructor method takes a list of Pokemon for the
    # player's team and a list of Pokemon for the opponents team
    # and an is_trainer flag
    def __init__(self, player: list[Pokemon], opponent: list[Pokemon], is_trainer: bool):
        # Initialize fields
        self.player = player
        self.opponent = opponent

        self.current = list(filter(lambda entry: entry.condition.health > 0, player))[0] # Player's first healthy Pokemon
        # Modify the player list so that the current Pokemon is first in the list
        self.player = self.player.copy()
        current_first = self.player[0]
        next_current_index = self.player.index(self.current)
        self.player[0] = self.current
        self.player[next_current_index] = current_first

        self.current_opponent = self.opponent[0]

        self.is_trainer = is_trainer
        self.turn = 0

        # Create socket for making TCP requests
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True
        self.logs = []

        # Add debugging print to notify that a connection was established
        print(f"Established connection with battle simulation server ({host}:{port})")

        # Start listening to messages
        self.start_listening()

        # Initialize list for listeners
        self.listeners: dict[BattleEvent, list[Callable[[...], None]]] = {}

        # Initialize a list to store all Pokemon relevant to this battle by their UUID
        self.pokemon: dict[str, Pokemon] = {}

        # Add each Pokemon from player's team
        for pokemon in self.player:
            self.pokemon[str(pokemon.uuid)] = pokemon

        # Add each Pokemon from the opponent's team
        for pokemon in self.opponent:
            self.pokemon[str(pokemon.uuid)] = pokemon

        # Attach a listener that makes the AI use a move each turn
        self.on(BattleEvent.TURN_CHANGE, self.ai_use_move)

    # Define a helper function to resolve status conditions
    def resolve_status_condition_message(self, condition):
        # Define a map
        conditions = {
            "brn": "was burned",
            "par": "was paralyzed",
            "slp": "fell asleep",
            "frz": "was frozen",
            "psn": "was poisoned",
            "tox": "was badly poisoned"
        }
        # Check if condition is in the map
        if condition in conditions:
            return conditions[condition]
        else:
            return f"was inflicted with {condition}" # Default message

    # Define an internal log method
    def __log(self, message: str):
        # Append to internal logs
        self.logs.append(message)
        # Call the log event
        self.__call_event(BattleEvent.LOG, message)

    # Define the listener callback for the socket
    def __listen(self):
        buffer = ""
        while True:
            try:
                data = self.socket.recv(4096)
            except Exception: # Socket has been closed
                break # Break out of the loop
            if not data:
                break
            buffer += data.decode('utf-8')
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                try:
                    # Load line as a JSON object
                    obj = json.loads(line.strip())

                    # Check if response has an error
                    if "error" in obj:
                        # Raise an error
                        raise Exception(obj["error"])

                    # Ensure every response has an action
                    if not "action" in obj:
                        # Raise an error
                        raise KeyError("Requests must specify an action")

                    # Check if this is a 'create' action
                    if obj["action"] == "create" and "battle_id" in obj:
                        self.battle_id = obj["battle_id"]
                        self.__log(f"Loaded battle: {self.battle_id}")
                        # Call STARTED event
                        self.__call_event(BattleEvent.STARTED)
                        # Send out starting Pokemon
                        self.__call_event(
                            BattleEvent.CURRENT_POKEMON_UPDATE,
                            self.current, self.current_opponent
                        )
                    elif obj["action"] == "message" and "output" in obj: # Check if this is a 'message' action
                        message = obj["output"]
                        self.__log(f"< {message}")

                        # Check if message contains any pipe deliminators
                        if "|" in message:
                            # Split the message by the pipe deliminator
                            args = obj["output"].split("|")

                            # Message action
                            action = args[1]

                            # Handle each action accordingly

                            if action == "move":
                                # Split arguments
                                user = self.get_pokemon_by_uuid(args[2])
                                move = args[3]
                                target = self.get_pokemon_by_uuid(args[4]) if len(args) >= 5 and ": " in args[4] else None
                                # Call the move event
                                self.__call_event(
                                    BattleEvent.MOVE,
                                    user, move, target,
                                    True if "[miss]" in message else False,
                                    True if "[still]" in message else False,
                                )
                            elif action == "-boost" or action == "-unboost":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                stat = args[3]
                                amount = int(args[4])
                                # Flip sign of 'amount' if action is unboost
                                amount *= -1
                                # Call the stat change event
                                self.__call_event(
                                    BattleEvent.STAT_CHANGE,
                                    target, stat, amount,
                                )
                            elif action == "turn":
                                # Split arguments
                                current_turn = int(args[2])
                                # Call the turn update event
                                self.__call_event(
                                    BattleEvent.TURN_CHANGE,
                                    current_turn
                                )
                            elif action == "switch":
                                # Split arguments
                                side = args[2].split(":")[0][1:-1] # Slice a string, ex: abcde -> bcd
                                target = self.get_pokemon_by_uuid(args[2])

                                # Check battler and assign current Pokemon
                                if side == Battler.PLAYER.value:
                                    self.current = target
                                elif side == Battler.AI.value:
                                    self.current_opponent = target

                                # Call the switch Pokemon event
                                self.__call_event(
                                    BattleEvent.CURRENT_POKEMON_UPDATE,
                                    self.current, self.current_opponent
                                )

                                # Split arguments to determine health
                                raw_health = args[4].split("/")
                                health = int(raw_health[0])
                                max_health = int(raw_health[1])

                                # Check if max health matches the Pokemon's health stat
                                # This is because HP is sent in two formats, current/max and
                                # current hp percent / 100
                                if max_health == target.get_max_health():
                                    # Determine targeted battler
                                    if target == self.current:
                                        battler = Battler.PLAYER
                                    else:
                                        battler = Battler.AI
                                    # Call a health update event
                                    self.__call_event(BattleEvent.HEALTH_UPDATE, battler, health)
                            elif action == "-damage" and "fnt" not in message:
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Split arguments to determine health
                                raw_health = args[3].split("/")
                                # Clean out the status condition
                                if " " in raw_health[1]:
                                    raw_health[1] = raw_health[1].split(" ")[0]
                                health = int(raw_health[0])
                                max_health = int(raw_health[1])

                                # Check if max health matches the Pokemon's health stat
                                # This is because HP is sent in two formats, current/max and
                                # current hp percent / 100
                                if max_health == target.get_max_health():
                                    # Determine targeted battler
                                    if target == self.current:
                                        battler = Battler.PLAYER
                                        # Update battle condition
                                        self.current.condition.health = health
                                    else:
                                        battler = Battler.AI
                                        # Update battle condition
                                        self.current_opponent.condition.health = health
                                    # Call a health update event
                                    self.__call_event(BattleEvent.HEALTH_UPDATE, battler, health)
                            elif action == "pp_update":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                raw_move_pps = args[3]
                                raw_pps = raw_move_pps.split(", ")
                                # Initialize PP dictionary
                                pp = {}
                                # Iterate each move
                                for data in raw_pps:
                                    # Split arguments
                                    move_name = data.split(": ")[0]
                                    # Iterate target's move set
                                    for move in target.get_moves():
                                        # Check if move_name matches this move loosely
                                        if move.replace("_", "").lower() == move_name.lower():
                                            # Move's match
                                            move_name = move
                                    pp_count = int(data.split(": ")[1])
                                    # Add pair to PP dictionary
                                    pp[move_name] = pp_count
                                # Call the PP update event
                                self.__call_event(BattleEvent.PP_UPDATE, target, pp)
                            elif action == "-crit":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.CRITICAL_HIT, target)
                            elif action == "-supereffective":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.SUPER_EFFECTIVE, target)
                            elif action == "-resisted":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.RESISTED, target)
                            elif action == "-immune":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.IMMUNE, target)
                            elif action == "faint":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Set Pokemon's health to 0
                                target.condition.health = 0
                                # Call the faint event
                                self.__call_event(BattleEvent.FAINTED, target)
                            elif action == "win":
                                # Split arguments
                                winner = args[2]
                                # Check if winner is 'player'
                                if winner == "player":
                                    won = True
                                else:
                                    won = False
                                # Call the event
                                self.__call_event(BattleEvent.END, won)
                            elif action == "-fail":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                action = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.FAILED, target, action)
                            elif action == "-block":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                effect = args[3]
                                move = args[4]
                                attacker = self.get_pokemon_by_uuid(args[5])
                                # Call the event
                                self.__call_event(BattleEvent.BLOCKED, target, effect, move, attacker)
                            elif action == "heal":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Split arguments to determine health
                                raw_health = args[3].split("/")
                                # Clean out the status condition
                                if " " in raw_health[1]:
                                    raw_health[1] = raw_health[1].split(" ")[0]
                                health = int(raw_health[0])
                                max_health = int(raw_health[1])

                                # Call the heal event
                                self.__call_event(BattleEvent.HEAL, target)

                                # Check if max health matches the Pokemon's health stat
                                # This is because HP is sent in two formats, current/max and
                                # current hp percent / 100
                                if max_health == target.get_max_health():
                                    # Determine targeted battler
                                    if target == self.current:
                                        battler = Battler.PLAYER
                                        # Update battle condition
                                        self.current.condition.health = health
                                    else:
                                        battler = Battler.AI
                                        # Update battle condition
                                        self.current_opponent.condition.health = health
                                    # Call a health update event
                                    self.__call_event(BattleEvent.HEALTH_UPDATE, battler, health)
                            elif action == "-status":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                status = self.resolve_status_condition_message(args[3])
                                # Call the event
                                self.__call_event(BattleEvent.STATUS_INFLICTED, target, status)
                            elif action == "-curestatus":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                status = self.resolve_status_condition_message(args[3])
                                # Call the event
                                self.__call_event(BattleEvent.STATUS_CURED, target, status)
                            elif action == "-cureteam":
                                # Split arguments
                                user = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.TEAM_STATUS_CURED, user)
                            elif action == "-swapboost":
                                # Split arguments
                                user = self.get_pokemon_by_uuid(args[2])
                                target = self.get_pokemon_by_uuid(args[3])
                                stats = args[4]
                                # Call the event
                                self.__call_event(BattleEvent.STAT_SWAPPED, user, target, stats)
                            elif action == "-invertboost":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.STAT_CHANGES_INVERTED, target)
                            elif action == "-clearboost":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.STAT_CHANGES_CLEARED, target)
                            elif action == "-clearallboost":
                                # Call the event
                                self.__call_event(BattleEvent.ALL_STAT_CHANGES_CLEARED)
                            elif action == "-clearpositiveboost":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                user = self.get_pokemon_by_uuid(args[3])
                                effect = self.get_pokemon_by_uuid(args[4])
                                # Call the event
                                self.__call_event(BattleEvent.CLEAR_POSITIVE_STAT_CHANGES, target, user, effect)
                            elif action == "-clearnegativeboost":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.CLEAR_NEGATIVE_STAT_CHANGES, target)
                            elif action == "-copyboost":
                                # Split arguments
                                user = self.get_pokemon_by_uuid(args[2])
                                target = self.get_pokemon_by_uuid(args[3])
                                # Call the event
                                self.__call_event(BattleEvent.COPY_STAT_CHANGES, user, target)
                            elif action == "-weather":
                                # Split arguments
                                weather = args[2]
                                # Call the event
                                self.__call_event(BattleEvent.WEATHER, weather)
                            elif action == "-fieldstart":
                                # Split arguments
                                condition = args[2]
                                # Call the event
                                self.__call_event(BattleEvent.FIELD_START, condition)
                            elif action == "-fieldend":
                                # Split arguments
                                condition = args[2]
                                # Call the event
                                self.__call_event(BattleEvent.FIELD_END, condition)
                            elif action == "-sidestart":
                                # Split arguments
                                side = args[2]
                                condition = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.SIDE_START, side, condition)
                            elif action == "-sideend":
                                # Split arguments
                                side = args[2]
                                condition = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.SIDE_END, side, condition)
                            elif action == "-swapsideconditions":
                                # Call the event
                                self.__call_event(BattleEvent.SWAP_SIDE_CONDITIONS)
                            elif action == "-start":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                effect = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.VOLATILE_STATUS_STARTED, target, effect)
                            elif action == "-end":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                effect = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.VOLATILE_STATUS_ENDED, target, effect)
                            elif action == "-ability" and "[from]" in message:
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                ability = args[3]
                                effect = args[4].replace("[from]", "")
                                # Call the event
                                self.__call_event(BattleEvent.ABILITY_CHANGED, target, ability, effect)
                            elif action == "-ability" and "[from]" not in message:
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                ability = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.ABILITY_ACTIVATED, target, ability)
                            elif action == "-endability":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                # Call the event
                                self.__call_event(BattleEvent.ABILITY_ENDED, target)
                            elif action == "-transform":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                species = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.TRANSFORM, target, species)
                            elif action == "-prepare" and len(args) == 3:
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                move = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.PREPARE_AGAINST_UNKNOWN, target, move)
                            elif action == "-prepare" and len(args) == 4:
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                move = args[3]
                                defender = args[4]
                                # Call the event
                                self.__call_event(BattleEvent.PREPARE_AGAINST_UNKNOWN, target, move, defender)
                            elif action == "-nothing":
                                # Call the event
                                self.__call_event(BattleEvent.NOTHING)
                            elif action == "-hitcount":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                hits = int(args[3])
                                # Call the event
                                self.__call_event(BattleEvent.MOVE_MULTI_HIT, target, hits)
                            elif action == "-singlemove":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                move = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.SINGLE_MOVE, target, move)
                            elif action == "-singleturn":
                                # Split arguments
                                target = self.get_pokemon_by_uuid(args[2])
                                move = args[3]
                                # Call the event
                                self.__call_event(BattleEvent.SINGLE_TURN, target, move)
                except json.JSONDecodeError as e:
                    self.__log(f"Failed to decode JSON: {e}")

    # Define the start listening function to attach the listen function
    def start_listening(self):
        listener_thread = threading.Thread(target=self.__listen, daemon=True)
        listener_thread.start()

    # Define the send request private method to send a request to the
    # battle simulation server
    def __send_request(self, request: dict[str, Any]):
        # Ensure socket is connected
        if not self.socket or not self.connected:
            raise ConnectionError("Not connected to socket")

        # Safely execute following code in a try-except block
        try:
            # Send the request as raw JSON
            request_json = json.dumps(request) + "\n"
            self.socket.send(request_json.encode())
        except Exception as e: # Catch any errors
            # Notify that an error occurred
            self.__log("An error occurred in the battle simulator connection")
            # Close the connection
            self.disconnect()
            raise

    # Define the send request private method to send a request to
    # the battle simulation server using the battle id
    def __send_identified_request(self, request: dict[str, Any]):
        # Ensure socket is connected
        if not self.socket or not self.connected:
            raise ConnectionError("Not connected to socket")

        # Safely execute following code in a try-except block
        try:
            # Send the request as raw JSON
            request["battle_id"] = self.battle_id
            request_json = json.dumps(request) + "\n"
            self.socket.send(request_json.encode())
        except Exception as e: # Catch any errors
            # Notify that an error occurred
            self.__log("An error occurred in the battle simulator connection")
            # Close the connection
            self.disconnect()
            raise e

    # Define the send request private method to send a request to
    # the battle simulation server using the battle id
    def __send_command(self, command: str):
        # Log the command that was sent
        self.__log(command)
        # Delegate to the send request function
        self.__send_identified_request({"action": "command", "command": command})

    # A public method to send commands
    def send_command_unsafe(self, command: str):
        # Delegate to private method
        self.__send_command(command)

    # Define a function to call an event
    def __call_event(self, event: BattleEvent, *args, **kwargs) -> Any:
        # Check if event type has any listeners
        if not event in self.listeners:
            return # Exit
        # Iterate all listeners
        for listener in self.listeners[event]:
            # Call the listener callback with *args and **kwargs
            listener(*args, **kwargs)

    # Define a function to get a Pokemon by their UUID
    def get_pokemon_by_uuid(self, uuid: str):
        # Check if 'uuid' contains a colon
        if ":" in uuid:
            # Split by the colin, remove all spaces and then reutnr the Pokemon by that identifier
            return self.pokemon[uuid.split(":")[1].replace(" ", "")]
        else: # otherwise, just return the Pokemon
            return self.pokemon[uuid]

    # Define a function to handle events
    def on(self, event: BattleEvent, listener: Callable[[...], None]):
        # Check if event type has any listeners
        if not event in self.listeners:
            self.listeners[event] = [] # Initialize
        # Add listener callback to list of listeners
        self.listeners[event].append(listener)

    # Define a function to get the team list of a side
    def get_team(self, battler: Battler):
        if battler == Battler.PLAYER:
            return self.player
        elif battler == Battler.AI:
            return self.opponent

    # Define the create battle function
    def create(self):
        # Send a create request
        self.__send_request({
            "action": "create"
        })

    # Define the start battle function
    def start(self):
        # Create a JSON body
        body = {"format": "nationaldexag"}
        # Send a start request
        self.__send_command(f">start {json.dumps(body)}")

    # Define a function to pack a team
    def pack_team(self, team: list[Pokemon]):
        # Pack each entry in the list
        packed = list(map(lambda pkm: pkm.pack_string(), team))
        # Return the packed list
        return packed

    # Define a function to send off the constructed teams
    def send_teams(self):
        # Construct teams
        player_team = {
            "name": "player",
            "team": "]".join(self.pack_team(self.player)),
        }
        opponent_team = {
            "name": "opponent",
            "team": "]".join(self.pack_team(self.opponent)),
        }

        # Send teams as commands
        self.__send_command(f">player p1 {json.dumps(player_team)}")
        self.__send_command(f">player p2 {json.dumps(opponent_team)}")

    # Define a function to send a team layout
    def send_layout(self, battler: Battler):
        # Get battler's team
        team = self.get_team(battler)
        # Initialize an empty string
        layout = ""
        # Iterate team's length amount of times
        for i in range(len(team)):
            # Append current index + 1 to the layout
            layout += str(i + 1)
        # Send the team layout command
        self.__send_command(f">p{battler.value} team {layout}")

    # Define a function to send both layouts
    def send_layouts(self):
        self.send_layout(Battler.PLAYER)
        self.send_layout(Battler.AI)

    # Define a function to select a move
    def select_move(self, battler: Battler, move: str | int):
        # Get battler's team
        self.get_team(battler)
        # Send the move selection command
        self.__send_command(f">p{battler.value} move {move}")

    # Define a function to catch the Pokemon
    def catch(self, ball: Ball):
        # Check if this battle is a trainer battle
        if self.is_trainer:
            # Throw an error
            raise Exception("Cannot use the 'catch' method in a trainer battle")

        # This formula is derived from Bulbapedia
        # https://bulbapedia.bulbagarden.net/wiki/Catch_rate

        # Define variables for the formula
        max_health = self.current_opponent.get_max_health()
        current_health = self.current_opponent.get_health()
        catch_rate = self.current_opponent.get_species().catch_rate
        ball_bonus = ball.value.handler(CatchContext(
            self.current,
            self.current_opponent,
            EncounterType.GRASS, # TODO Implement other encounter types
            self.turn
        ))
        status_bonus = 1  # TODO Implement status condition bonuses
        other_modifiers = 1

        # Calculate formula
        a = (((3 * max_health - 2 * current_health) * catch_rate * ball_bonus * status_bonus * other_modifiers) / (
                    3 * max_health))

        # Apply the catch rate modifier
        a *= holder.catch_rate_mod

        # Initialize variables
        is_success = False
        shakes = 0

        if a >= 255:
            # Automatic guaranteed catch
            is_success = True
            shakes = 4
        else:
            # Calculate 'b'
            b = 1048560 / math.sqrt(math.sqrt(16711680 / a))

            # Simulate four shakes
            for _ in range(4):
                # Generate a random number
                roll = random.randint(0, 65535)
                # Check if shake is successful (b must be greater than roll)
                if roll < b:
                    shakes += 1
                else:
                    break # Don't calculate next shake

            # Catch is successful if four shakes were passed
            is_success = shakes == 4

        # Call the event
        self.__call_event(BattleEvent.CATCH, is_success, ball, shakes - 1 if shakes > 0 else shakes)

        # Send command
        if is_success:
            # Send a capture command
            self.__send_command(f">capture p{Battler.AI.value}a")
        else:
            # Send a pass command
            self.__send_command(f">p{Battler.PLAYER.value} pass")

    # Define a function to make the AI use a move
    def ai_use_move(self, _: int):
        # Initialize a move map
        moves = {}
        # Iterate each of the AI's moves
        for move in self.current_opponent.condition.move_set:
            # If we don't have enough PP then skip
            if move.pp <= 0:
                continue

            # Obtain the move object
            move_obj = holder.get_move(move.name)

            # Calculate the STAB (Same-Type-Attack-Bonus) modifier
            stab_bonus = (1.5 if move_obj.type in self.current_opponent.get_species().types else 1)
            # Determine the power of the move
            power = move_obj.power if move_obj.power is not None else 0
            # Calculate the effective power of this move and place it in the map
            moves[move.name] = power * stab_bonus
        # Chance of 30%
        if random.random() <= 0.3:
            # Shuffle the moves map for some randomness
            items = list(moves.items())
            random.shuffle(items)
            moves = dict(items)
        else: # Otherwise
            # Sort the moves by highest power
            moves = dict(sorted(moves.items(), key=lambda item: int(item[1]), reverse=True))
        # Get first move
        selected_move, _ = next(iter(moves.items()))
        # Get the index of the selected move in the Pokemon's move set
        move_index = self.current_opponent.get_moves().index(selected_move)
        # Select the move
        self.select_move(Battler.AI, move_index + 1)

    # Define a function to switch current Pokemon
    def switch(self, battler: Battler, pokemon: Pokemon):
        # Send the command
        self.__send_command(f">p{battler.value} switch {pokemon.uuid}")

    # Define a function to disconnect the socket
    def disconnect(self):
        # Check if there is an active socket
        if self.socket:
            # Close and remove the socket
            self.socket.close()
            self.socket = None
        # Mark battle as unconnected
        self.connected = False