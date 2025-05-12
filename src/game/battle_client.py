# This file defines the 'BattleClient' a special class that communicates with a
# battle simulation server to handle Pokemon battle processing and simulation
import json
# Imports

import socket
from typing import Any

from src.pokemon.pokemon import Pokemon

# Define constants for battle simulation server
host = "127.0.0.1"
port = 8970
token = "demo_token_12345"

# Define the 'BattleClient' class
class BattleClient:
    def __init__(self, player: list[Pokemon], opponent: list[Pokemon]):
        # Initialize fields
        self.player = player
        self.opponent = opponent

        # Create socket for making TCP requests
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.connected = True

        # Add debugging print to notify that a connection was established
        print(f"Established connection with battle simulation server ({host}:{port})")

    # Define the '_send_request' internal method to send a request to the
    # battle simulation server
    def _send_request(self, request: dict[str, Any]) -> dict[str, Any]:
        # Ensure socket is connected
        if not self.socket or not self.connected:
            raise ConnectionError("Not connected to socket")

        # Specify authentication token in request
        request['token'] = token

        # Safely execute following code in a try-except block
        try:
            # Send the request as raw JSON
            request_json = json.dumps(request) + "\n"
            self.socket.sendall(request_json.encode())

            # Retrieve and process the response
            response_data = b''
            while b'\n' not in response_data:
                # Process response in 4096 bytes (4 KB) chunks
                chunk = self.socket.recv(4096)
                # Check if chunk is empty
                if not chunk:
                    # Break reading loop
                    break
                # Append chunk to response_data
                response_data += chunk

            # Parse the response as a JSON object
            response_json = response_data.decode().strip()
            response = json.loads(response_json)

            # Return the response object
            return response
        except Exception as e: # Catch any errors
            # Notify that an error occurred
            print("An error occurred in the battle simulator connection")
            # Close the connection
            self.disconnect()
            raise

    # Define the 'start_battle' method to start the battle
    def start_battle(self):
        # Build a request to start the battle with
        request = {
            'action': 'create_battle',
            'format': 'nationaldexag',
            'p1spec': [],
            'p2spec': []
        }

    # Define the 'disconnect' function
    def disconnect(self):
        # Check if a socket was created
        if self.socket:
            # Close the socket
            self.socket.close()
            # Add debugging print
            print(f"Closed connection with battle simulation server ({host}:{port})")
        # Reset battle socket fields
        self.socket = None
        self.connected = False