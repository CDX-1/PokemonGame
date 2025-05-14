from src import holder
from src.game.battle_client import BattleClient, Battler, BattleEvent

import time

from src.pokemon.pokemon import Pokemon
from src.pokemon.types.stat import Stat


def test1():
    print(holder.get_species("charmander").spawn(10).pack_string())

def test():
    client = BattleClient(
        [
            holder.get_species("charmander").spawn(10)
        ],
        [
            holder.get_species("pidgey").spawn(8)
        ]
    )

    def on_start():
        client.start()
        client.send_teams()
        client.send_layouts()
        client.select_move(Battler.PLAYER, 1)
        client.select_move(Battler.AI, 1)

    def on_move(user: Pokemon, move: str, target: Pokemon, miss: bool, still: bool):
        print(f"{user.nickname} used {move} on {target.nickname}")

    def on_stat_change(target: Pokemon, stat: str, amount: int):
        verb = "increased" if amount > 0 else "decreased"
        if amount <= 0:
            amount *= -1
        print(f"{target.nickname}'s {stat} has {verb} by {amount}")

    client.on(BattleEvent.STARTED, on_start)
    client.on(BattleEvent.MOVE, on_move)
    client.on(BattleEvent.STAT_CHANGE, on_stat_change)
    client.create()