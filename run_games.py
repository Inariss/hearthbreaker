import json
from hearthbreaker.agents.basic_agents import RandomAgent, DoNothingAgent, OpponentAgent
from hearthbreaker.agents.test_agent import TalkativeAgent
from hearthbreaker.agents.aggressive_agent import AggressiveAgent
from hearthbreaker.agents.controlling_agent import ControllingAgent
from hearthbreaker.agents.mcts_agent import MCTSAgent
from hearthbreaker.cards.heroes import Jaina, Malfurion, hero_for_class
from hearthbreaker.constants import CHARACTER_CLASS
from hearthbreaker.engine import Game, Deck, card_lookup
from hearthbreaker.cards import *
import timeit
from hearthbreaker.agents.mcts_agent import MCTSAgent



def load_deck(filename):
    cards = []

    with open(filename, "r") as deck_file:
        contents = deck_file.read()
        items = contents.splitlines()
        for line in items[0:]:
            parts = line.split(" ", 1)
            count = int(parts[0])
            for i in range(0, count):
                card = card_lookup(parts[1])
                cards.append(card)

    if len(cards) > 20:
        pass

    return cards


def do_stuff():
    _count = 0

    def play_game():
        nonlocal _count
        _count += 1
        new_game = game.copy()
        try:
            winner = new_game.start()
            print("Winner: ",winner)

            print()
            print("# " * 27, " GAME OVER ", " #" * 27)
            print(new_game.players[0], "has", new_game.players[0].hero.health, "life points,\t", end='')
            print(new_game.players[1], "has", new_game.players[1].hero.health, "life points")
            print(winner, 'won the game (', winner.agent, ')')
            print("# " * 61, "\n")

        except Exception as e:
            # print(json.dumps(new_game.__to_json__(), default=lambda o: o.__to_json__(), indent=1))
            # print(new_game._all_cards_played)
            raise e

        del new_game

        if _count % 1000 == 0:
            print("---- game #{} ----".format(_count))

    cards = load_deck("mage3.hsdeck")
    deck1 = Deck(cards, Jaina())
    deck2 = Deck(cards, Malfurion())
    game = Game([deck1, deck2], [MCTSAgent(5), RandomAgent()])
    # game = Game([deck1, deck2], [AggressiveAgent(), RandomAgent()])

    # game = Game([deck1, deck2], [ControllingAgent(), RandomAgent()])
    # game = Game([deck1, deck2], [TalkativeAgent(), RandomAgent()])
    # game = Game([deck1, deck2], [RandomAgent(), RandomAgent()])
    print(timeit.timeit(play_game, 'gc.enable()', number=1))


if __name__ == "__main__":
    do_stuff()
