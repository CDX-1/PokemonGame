#!/usr/bin/env python3
"""
Pokémon Battle Client

A Python client that connects to the Pokémon Battle TCP Server
to simulate Pokémon battles.
"""

import socket
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PokemonBattleClient')


class PokemonBattleClient:
    """Client for interacting with the Pokémon Battle TCP Server."""

    def __init__(self, host: str = '127.0.0.1', port: int = 8970, token: str = 'demo_token_12345'):
        """
        Initialize the battle client.

        Args:
            host: Server hostname
            port: Server port
            token: Authentication token
        """
        self.host = host
        self.port = port
        self.token = token
        self.socket = None
        self.connected = False
        self.current_battle_id = None

    def connect(self) -> bool:
        """
        Connect to the battle server.

        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Close the connection to the server."""
        if self.socket:
            self.socket.close()
            logger.info("Disconnected from server")
        self.connected = False
        self.socket = None

    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the server and get the response.

        Args:
            request: The request to send

        Returns:
            The server's response

        Raises:
            ConnectionError: If not connected to the server
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected to server")

        # Add authentication token
        request['token'] = self.token

        try:
            # Send request
            request_json = json.dumps(request) + '\n'
            self.socket.sendall(request_json.encode())

            # Get response
            response_data = b''
            while b'\n' not in response_data:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            # Parse response
            response_json = response_data.decode().strip()
            response = json.loads(response_json)
            return response

        except Exception as e:
            logger.error(f"Error in communication: {e}")
            self.disconnect()
            raise

    def create_battle(self, format_name: str = 'gen9randombattle',
                      p1_spec: Dict[str, Any] = None,
                      p2_spec: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new battle on the server.

        Args:
            format_name: The battle format (e.g., 'gen9randombattle')
            p1_spec: Player 1 specification
            p2_spec: Player 2 specification

        Returns:
            Response from the server with battle details
        """
        # Use default specifications if none provided
        if p1_spec is None:
            p1_spec = {'name': 'Player 1'}
        if p2_spec is None:
            p2_spec = {'name': 'Player 2'}

        request = {
            'action': 'create_battle',
            'format': format_name,
            'p1spec': p1_spec,
            'p2spec': p2_spec
        }

        response = self._send_request(request)

        if response.get('success'):
            self.current_battle_id = response.get('battleId')
            logger.info(f"Battle created with ID: {self.current_battle_id}")
        else:
            logger.error(f"Failed to create battle: {response.get('error')}")

        return response

    def create_battle_with_teams(self,
                                 format_name: str,
                                 p1_name: str,
                                 p1_team: List[Dict[str, Any]],
                                 p2_name: str,
                                 p2_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a battle with specific teams.

        Args:
            format_name: The battle format (e.g., 'gen9customgame')
            p1_name: Player 1's name
            p1_team: Player 1's team data
            p2_name: Player 2's name
            p2_team: Player 2's team data

        Returns:
            Response from the server with battle details
        """
        p1_spec = {
            'name': p1_name,
            'team': p1_team
        }

        p2_spec = {
            'name': p2_name,
            'team': p2_team
        }

        return self.create_battle(format_name, p1_spec, p2_spec)

    def process_turn(self, actions: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a turn in the current battle.

        Args:
            actions: Dictionary mapping player IDs to their actions
                Example: {
                    'p1': {'type': 'move', 'moveIndex': 0},
                    'p2': {'type': 'switch', 'pokeIndex': 2}
                }

        Returns:
            Response from the server with battle updates
        """
        if not self.current_battle_id:
            raise ValueError("No active battle")

        request = {
            'action': 'process_turn',
            'battleId': self.current_battle_id,
            'actions': actions
        }

        response = self._send_request(request)

        if not response.get('success') and 'error' in response:
            logger.error(f"Turn processing failed: {response.get('error')}")

        return response

    def get_battle_state(self) -> Dict[str, Any]:
        """
        Get the current state of the battle.

        Returns:
            Current battle state data
        """
        if not self.current_battle_id:
            raise ValueError("No active battle")

        request = {
            'action': 'get_battle_state',
            'battleId': self.current_battle_id
        }

        response = self._send_request(request)

        if not response.get('success') and 'error' in response:
            logger.error(f"Failed to get battle state: {response.get('error')}")

        return response

    def end_battle(self) -> Dict[str, Any]:
        """
        End the current battle.

        Returns:
            Response from the server
        """
        if not self.current_battle_id:
            raise ValueError("No active battle")

        request = {
            'action': 'end_battle',
            'battleId': self.current_battle_id
        }

        response = self._send_request(request)

        if response.get('success'):
            logger.info(f"Battle {self.current_battle_id} ended")
            self.current_battle_id = None
        else:
            logger.error(f"Failed to end battle: {response.get('error')}")

        return response