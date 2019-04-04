import abc
import copy

import random
from hearthbreaker.cards.base import Card


class Agent(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def do_card_check(self, cards):
        pass

    @abc.abstractmethod
    def do_turn(self, player):
        pass

    @abc.abstractmethod
    def choose_target(self, targets):
        pass

    @abc.abstractmethod
    def choose_index(self, card, player):
        pass

    @abc.abstractmethod
    def choose_option(self, options, player):
        pass

    def filter_options(self, options, player):
        if isinstance(options[0], Card):
            return [option for option in options if option.can_choose(player)]
        return [option for option in options if option.card.can_choose(player)]


class DoNothingAgent(Agent):
    def __init__(self):
        self.game = None

    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        print("TURN OF DO NOTHING AGENT")
        print('---\nTurn of', player)
        pass

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class PredictableAgent(Agent):
    def do_card_check(self, cards):
        return [True, True, True, True]

    def do_turn(self, player):
        done_something = True

        if player.hero.power.can_use():
            player.hero.power.use()

        if player.hero.can_attack():
            player.hero.attack()

        while done_something:
            done_something = False
            for card in player.hand:
                if card.can_use(player, player.game):
                    player.game.play_card(card)
                    done_something = True
                    break
        # absolutna kopia calego obiektu, nowe wartości stworzone, stary obiekt nie jest modyfikowany
        for minion in copy.copy(player.minions):
            if minion.can_attack():
                minion.attack()

    def choose_target(self, targets):
        return targets[0]

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


class RandomAgent(DoNothingAgent):
    def __init__(self):
        super().__init__()

    def do_card_check(self, cards):
        return [True, True, True, True]

    def print_info_about_turn(self, player):
        print("\nSTART A TURN OF RANDOM AGENT", player)
        print("\tHero:", player.hero.card)
        print("\tHealth:", player.hero.health)
        print("\tOpponent's health:", player.game.other_player.hero.health)
        # print("My current mana:", player.mana)

        # print("Cards on hand:\n\t", end='')
        # if player.hand:
        #     cards_details = [str(card.name) + " (" + str(card.mana) + " mana)" for card in player.hand]
        #     print(*cards_details, sep='\n\t')
        # else:
        #     print('[]')
        #
        # print("Cards on table:\n\t", end='')
        # if player.minions:
        #     print(*player.minions, sep='\n\t')
        # else:
        #     print('[]')
        #
        # print("<-- info <--")

    def do_turn(self, player):
        # self.print_info_about_turn(player)
        while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            if player.hero.can_attack():
                attack_minions.append(player.hero)
            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game) and card.mana<=player.mana, player.hand)]

            # print(">>> PLAYING CARDS FROM HAND >>>")
            # # possible_cards_to_use = [card for card in player.hand if (card.can_use(player, player.game))]
            # print(">>> Possible cards to use: ", playable_cards)


            if player.hero.power.can_use():
                possible_actions = len(attack_minions) + len(playable_cards) + 1
            else:
                possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                action = random.randint(0, possible_actions - 1)
                if player.hero.power.can_use() and action == possible_actions - 1:
                    player.hero.power.use()
                elif action < len(attack_minions):
                    attack_minions[action].attack()
                else:
                    card_to_be_played = playable_cards[action - len(attack_minions)]
                    player.game.play_card(card_to_be_played)
                    # print(">>> Using card from hand:\n>>>    ", card_to_be_played)
                    # print("<<< PLAYING CARDS FROM HAND <<<")
            else:
                # print("<<< PLAYING CARDS FROM HAND <<<")
                return

    def choose_target(self, targets):
        # print("--- CHOOSING TARGET ---\n--- Choosing target from list:\n---    ", end='')
        # print(*targets, sep='\n---    ')
        target_chosen = targets[random.randint(0, len(targets) - 1)]
        # print("--- Chosen target:\n---   ", target_chosen)
        return target_chosen

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]


class OpponentAgent(DoNothingAgent):
    def __init__(self):
        super().__init__()

    def do_card_check(self, cards):
        return [True, True, True, True]

    def print_info_about_turn(self, player):
        print("\nSTART A TURN OF OPPONENT AGENT", player)
        print("My",player.hero)
        print("Opponent's hero:", player.game.other_player.hero.card)
        print("My mana:", player.mana)

        print("Cards on hand:\n\t", end='')
        if player.hand:
            cards_details = [str(card.name) + " (" + str(card.mana) + " mana)" for card in player.hand]
            print(*cards_details, sep='\n\t')
        else:
            print('[]')

        print("Cards on table:\n\t", end='')
        if player.minions:
            print(*player.minions, sep='\n\t')
        else:
            print('[]')

        print("<-- info <--")

    def do_turn(self, player):
        attack = []
        play = []
        self.print_info_about_turn(player)
        while True:
            attack_minions = [minion for minion in filter(lambda minion: minion.can_attack(), player.minions)]
            if player.hero.can_attack():
                attack_minions.append(player.hero)

            playable_cards = [card for card in filter(lambda card: card.can_use(player, player.game) and card.mana<=player.mana, player.hand)]
            if player.hero.power.can_use():
                possible_actions = len(attack_minions) + len(playable_cards) + 1
            else:
                possible_actions = len(attack_minions) + len(playable_cards)
            if possible_actions > 0:
                action = random.randint(0, possible_actions - 1)
                if player.hero.power.can_use() and action == possible_actions - 1:
                    player.hero.power.use()
                elif action < len(attack_minions):
                    attack_minions[action].attack()

                else:
                    card_to_be_played = playable_cards[action - len(attack_minions)]
                    player.game.play_card(card_to_be_played)
                    play.append(card_to_be_played)

            else:
                print("Opponent agent turn:\n\tcards:",play, "\n\tattacks:", attack)
                return

    def choose_target(self, targets):
        # print("--- CHOOSING TARGET ---\n--- Choosing target from list:\n---    ", end='')
        # print(*targets, sep='\n---    ')
        target_chosen = targets[random.randint(0, len(targets) - 1)]
        # print("--- Chosen target:\n---   ", target_chosen)
        return target_chosen

    def choose_index(self, card, player):
        return random.randint(0, len(player.minions))

    def choose_option(self, options, player):
        options = self.filter_options(options, player)
        return options[random.randint(0, len(options) - 1)]

