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

from src.pokemon.pokemon import Pokemon
from src.pokemon.types.ball import Ball
from src.pokemon.types.catch_context import CatchContext
from src.pokemon.types.encounter_type import EncounterType
from src.pokemon.types.stat import Stat

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
    CATCH_SUCCESS = "catch_success" # A successful catch
    CATCH_FAILURE = "catch_failure" # A failed catch
    TURN_CHANGE = "turn_change" # The turn counter has updated
    PP_UPDATE = "pp_update" # Move PP has been updated
    CURRENT_POKEMON_UPDATE = "current_pokemon_update" # A Pokemon on the field has been updated

# Define the 'BattleClient' class
class BattleClient:
    # Class constructor method takes a list of Pokemon for the
    # player's team and a list of Pokemon for the opponents team
    # and an is_trainer flag
    def __init__(self, player: list[Pokemon], opponent: list[Pokemon], is_trainer: bool):
        # Initialize fields
        self.player = player
        self.opponent = opponent

        self.current = self.player[0]
        self.current_opponent = self.opponent[0]

        self.is_trainer = is_trainer
        self.turn = 0

        # Create socket for making TCP requests
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True

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

    # Define the listener callback for the socket
    def __listen(self):
        buffer = ""
        while True:
            data = self.socket.recv(4096)
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
                        print(f"Loaded battle: {self.battle_id}")
                        # Call STARTED event
                        self.__call_event(BattleEvent.STARTED)
                    elif obj["action"] == "message" and "output" in obj: # Check if this is a 'message' action
                        message = obj["output"]

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
                                target = self.get_pokemon_by_uuid(args[4])
                                # Call the move event
                                self.__call_event(
                                    BattleEvent.MOVE,
                                    user, move, target,
                                    True if "|[miss]|" in message else False,
                                    True if "|[still]|" in message else False,
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
                                # Iterate battlers
                                for battler in Battler:
                                    if battler.value == side:
                                        side = battler
                                        break
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
                    else:
                        # Print raw message in edge-cases
                        print(obj)

                except json.JSONDecodeError as e:
                    print("Failed to decode JSON:", e)

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
            print("An error occurred in the battle simulator connection")
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
            print("An error occurred in the battle simulator connection")
            # Close the connection
            self.disconnect()
            raise e

    # Define the send request private method to send a request to
    # the battle simulation server using the battle id
    def __send_command(self, command: str):
        # Log the sent command
        print(command)
        # Delegate to the send request function
        self.__send_identified_request({"action": "command", "command": command})

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
        max_health = self.current_opponent.get_stat(Stat.HP)
        current_health = self.current_opponent.condition.health
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

        # Declare the event type depending on whether the catch was successful or not
        event_type = BattleEvent.CATCH_SUCCESS if is_success else BattleEvent.CATCH_FAILURE

        # Call the event
        self.__call_event(event_type, is_success, shakes - 1 if shakes > 0 else shakes)

    # Define a function to disconnect the socket
    def disconnect(self):
        # Check if there is an active socket
        if self.socket:
            # Close and remove the socket
            self.socket.close()
            self.socket = None
        # Mark battle as unconnected
        self.connected = False