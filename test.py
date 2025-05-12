#!/usr/bin/env python3
"""
Test script for the Pokémon Battle TCP Server.
This script runs a simple battle to verify the server is working correctly.
"""

import sys
import time
import json
from pokemon_battle_client import PokemonBattleClient


def run_test_battle():
    """
    Run a test battle to verify server functionality.
    """
    print("Pokémon Battle Server Test")
    print("=========================")

    # Create client
    print("Connecting to server...")
    client = PokemonBattleClient()

    try:
        # Connect to server
        if not client.connect():
            print("ERROR: Failed to connect to server.")
            return False

        print("Successfully connected to server.")

        # Create a random battle
        print("\nCreating random battle...")
        battle_response = client.create_battle('gen9randombattle')

        if not battle_response.get('success'):
            print(f"ERROR: Failed to create battle: {battle_response.get('error')}")
            return False

        battle_id = client.current_battle_id
        print(f"Battle created with ID: {battle_id}")

        # Pause to allow battle initialization
        time.sleep(1)

        # Get initial battle state
        print("\nFetching initial battle state...")
        state_response = client.get_battle_state()

        if not state_response.get('success'):
            print(f"ERROR: Failed to get battle state: {state_response.get('error')}")
            return False

        # Print battle state details
        battle_state = state_response.get('battleState', {})

        print("\nBattle State Details:")
        print(f"Turn: {battle_state.get('turn', 0)}")

        p1 = battle_state.get('p1', {})
        p2 = battle_state.get('p2', {})

        print(f"\nPlayer 1: {p1.get('name', 'Unknown')}")
        print("Team:")
        for i, pokemon in enumerate(p1.get('team', [])):
            status = "ACTIVE" if pokemon.get('active') else "Benched"
            print(
                f"  {i + 1}. {pokemon.get('species', 'Unknown')} - HP: {pokemon.get('hp', '?')}/{pokemon.get('maxhp', '?')} - {status}")
            for move in pokemon.get('moves', []):
                print(f"     - {move.get('name', '?')} ({move.get('pp', '?')}/{move.get('maxpp', '?')})")

        print(f"\nPlayer 2: {p2.get('name', 'Unknown')}")
        print("Team:")
        for i, pokemon in enumerate(p2.get('team', [])):
            status = "ACTIVE" if pokemon.get('active') else "Benched"
            print(
                f"  {i + 1}. {pokemon.get('species', 'Unknown')} - HP: {pokemon.get('hp', '?')}/{pokemon.get('maxhp', '?')} - {status}")
            for move in pokemon.get('moves', []):
                print(f"     - {move.get('name', '?')} ({move.get('pp', '?')}/{move.get('maxpp', '?')})")

        # Process a turn
        print("\nProcessing turn 1...")
        turn_response = client.process_turn({
            'p1': {'type': 'move', 'moveIndex': 0},
            'p2': {'type': 'move', 'moveIndex': 0}
        })

        if not turn_response.get('success'):
            print(f"ERROR: Failed to process turn: {turn_response.get('error')}")
            return False

        print("Turn processed successfully!")

        # Print battle updates
        updates = turn_response.get('updates', [])
        if updates:
            print("\nBattle Updates:")
            for update in updates:
                print(f"  - {update.get('type')}: {update.get('data')}")

        # Get updated battle state
        print("\nFetching updated battle state...")
        state_response = client.get_battle_state()

        if not state_response.get('success'):
            print(f"ERROR: Failed to get updated battle state: {state_response.get('error')}")
            return False

        battle_state = state_response.get('battleState', {})
        is_over = battle_state.get('isOver', False)

        if is_over:
            print(f"\nBattle ended. Winner: {battle_state.get('winner', 'Unknown')}")
        else:
            print(f"\nBattle continues. Current turn: {battle_state.get('turn', '?')}")

        if not end_response.get('success'):
            print(f"ERROR: Failed to end battle: {end_response.get('error')}")
            return False

        print("Battle ended successfully!")
        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    finally:
        # Ensure we disconnect
        print("\nDisconnecting from server...")
        client.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    success = run_test_battle()
    sys.exit(0 if success else 1)