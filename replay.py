import re
import hsgame
from hsgame.constants import CHARACTER_CLASS
import hsgame.game_objects

__author__ = 'Daniel'


class ReplayException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ProxyCharacter:

    def __init__(self, character_ref, game=None):
        if type(character_ref) is str:
            self.character_ref = character_ref
        elif type(character_ref) is hsgame.game_objects.Player:
            if character_ref == game.players[0]:
                self.character_ref = "p1"
            else:
                self.character_ref = "p2"
        elif type(character_ref) is hsgame.game_objects.Minion:
            if character_ref.player == game.players[0]:
                self.character_ref = "p1:" + str(character_ref.index)
            else:
                self.character_ref = "p2:" + str(character_ref.index)

    def resolve(self, game):
        ref = self.character_ref.split(':')
        if ref[0] == "p1":
            char = game.players[0]
        else:
            char = game.players[1]
        if len(ref) > 1:
            return char.minions[int(ref[1])]

        return char

    def __str__(self):
        return self.character_ref

    def to_output(self):
        return str(self)


class ProxyCard:

    def __init__(self, card_reference, game=None):
        self.card_ref = -1
        if type(card_reference) is int:
            self.card_ref = int(card_reference)
        else:
            index = 0
            for card in game.current_player.hand:
                if card is card_reference:
                    self.card_ref = index
                    break
                index += 1

        if self.card_ref < 0:
            raise ReplayException("Could not find card in hand")

        self.targettable = False

    def resolve(self, game):
        return game.current_player.hand[self.card_ref]

    def __str__(self):
        return str(self.card_ref)

    def to_output(self):
        return str(self)





class ReplayAction:
        def play(self):
            pass


class SpellAction(ReplayAction):
    def __init__(self, card, target=None, game=None):
        self.card = card
        if target is not None:
            self.target = ProxyCharacter(target, game)
        else:
            self.target = None

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve()
        self.card.resolve().play()
        game.current_player.agent.next_target = None

    def to_output_string(self):
        if self.target is not None:
            return 'play({0},{1})'.format(self.card.to_output(), self.target.to_output())
        return 'play({0})'.format(self.card.to_output())


class MinionAction(ReplayAction):
    def __init__(self, card, index, target=None, game=None):
        self.card = card
        self.index = index
        if target is not None:
            self.target = ProxyCharacter(target, game)
        else:
            self.target = None

    def to_output_string(self):
        if self.target is not None:
            return 'summon({0},{1},{2})'.format(self.card.to_output(), self.index, self.target.to_output())
        return 'summon({0},{1})'.format(self.card.to_output(), self.index)


    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)

        game.current_player.agent.next_target = self.index
        self.card.resolve(game).use(game.current_player, game)
        game.current_player.agent.next_target = None


class AttackAction(ReplayAction):
    def __init__(self, character, target, game=None):
        self.character = ProxyCharacter(character, game)
        self.target = ProxyCharacter(target, game)

    def to_output_string(self):
            return 'attack({0},{1})'.format(self.character.to_output(), self.target.to_output())

    def play(self, game):
        game.current_player.agent.next_target = self.target.resolve()
        self.character.resolve(game).attack()
        game.current_player.agent.next_target = None


class PowerAction(ReplayAction):
    def __init__(self, target=None, game=None):
        self.target = target
        if target is not None:
            self.target = ProxyCharacter(target, game)
        else:
            self.target = None
        self.game = game

    def to_output_string(self):
        if self.target is not None:
            return 'power({0})'.format(self.target.to_output())
        else:
            return 'power()'

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve()
        self.character.resolve().attack()
        game.current_player.agent.next_target = None


class TurnEndAction(ReplayAction):
    def __init__(self, game=None):
        pass

    def to_output_string(self):
        return 'end()'

    def play(self, game):
        pass



class Replay:

    def __init__(self):
        self.actions = []
        self.random_numbers = []
        self.last_card = None
        self.card_class = None
        self.last_target = None
        self.last_index = None
        self.decks = []
        self.keeps = []

    def save_decks(self, deck1, deck2):
        self.decks = [deck1, deck2]

    def record_random(self, result):
        self.random_numbers.append(result)

    def record_turn_end(self, game):
        self._save_played_card(game)
        self.actions.append(TurnEndAction())

    def _save_played_card(self, game):
        if self.last_card is not None:
            if issubclass(self.card_class, hsgame.game_objects.MinionCard):
                if self.last_card.targettable:
                    self.actions.append(MinionAction(self.last_card, self.last_index, self.last_target, game))
                    self.last_card = None
                    self.last_index = None
                    self.last_target = None
                else:
                    self.actions.append(MinionAction(self.last_card, self.last_index, game=game))
                    self.last_card = None
                    self.last_index = None
            else:
                if self.last_card.targettable:
                    self.actions.append(SpellAction(self.last_card, self.last_target, game))
                    self.last_card = None
                    self.last_target = None
                else:
                    self.actions.append(SpellAction(self.last_card, game=game))
                    self.last_card = None

    def record_card_played(self, card, game):
        self._save_played_card(game)
        self.last_card = ProxyCard(card, game)
        self.last_card.targettable = card.targettable
        self.card_class = type(card)

    def record_attack(self, target, attacker, game):
        self._save_played_card(game)
        self.actions.append(AttackAction(attacker, target, game))

    def record_power(self, game):
        self._save_played_card(game)
        self.actions.append(PowerAction(game=game))

    def record_power_target(self, target, game):
        self.actions[len(self.actions) - 1].target = ProxyCharacter(target, game)

    def record_kept_index(self, cards, card_index, game):
        k_arr = []
        for index in range(0, len(cards)):
            if card_index[index]:
                k_arr.append(index)
        self.keeps.append(k_arr)

    def write_replay(self, file):

        # Mostly for testing, this function will check if the deck is made up of a repeating pattern
        # and if so, shorten the output, since the parser will generate the pattern from a shorter sample
        def shorten_deck(cards):
            for pattern_length in range(1, 15):
                matched = True
                for index in range(pattern_length, 30):
                    if type(cards[index % pattern_length]) is not type(cards[index]):
                        matched = False
                        break
                if matched:
                    return cards[0:pattern_length]


        if 'write' not in dir(file):
            writer = open(file, 'w')
        else:
            writer = file

        for deck in self.decks:
            writer.write("deck(")
            writer.write(CHARACTER_CLASS.to_str(deck.character_class))
            writer.write(",")
            writer.write(",".join([card.name for card in shorten_deck(deck.cards)]))
            writer.write(")\n")

        writer.write("random(")
        writer.write(",".join([str(num) for num in self.random_numbers]))
        writer.write(")\n")

        for keep in self.keeps:
            writer.write("keep(")
            writer.write(",".join([str(k) for k in keep]))
            writer.write(")\n")

        for action in self.actions:
            writer.write(action.to_output_string() + "\n")

    def parse_replay(self, replayfile):

        if 'read' not in dir(replayfile):
            replayfile = open(replayfile, 'r')
        line_pattern = re.compile("([^\(]*)\(([^)]*)\)")
        args_split = re.compile("\s*,\s*")
        for line in replayfile:
            (action, args) = line_pattern.match(line).group(1, 2)
            args = args_split.split(args)
            if action == 'play':
                card = int(args[0])
                if len(args) > 1:
                    target = args[1]
                else:
                    target = None
                self.actions.append(SpellAction(ProxyCard(card), target))

            elif action == 'summon':
                card = int(args[0])

                index = int(args[1])

                if len(args) > 2:
                    target = args[2]
                else:
                    target = None

                self.actions.append(MinionAction(ProxyCard(card), index, target))
            elif action == 'attack':
                self.actions.append(AttackAction(args[0], args[1]))
            elif action == 'power':
                if len(args) > 0:
                    self.actions.append(PowerAction(args[0]))
            elif action == 'end':
                self.actions.append(TurnEndAction())
            elif action == 'random':
                if len(self.random_numbers) > 0:
                    raise ReplayException("Only one random number list per file")
                if len(args[0]) > 0:
                    self.random_numbers = [int(num) for num in args]
            elif action == 'deck':
                if len(self.decks) > 1:
                    raise ReplayException("Maximum of two decks per file")
                deck_size = len(args) - 1
                cards = [hsgame.game_objects.card_lookup(args[1 + index % (deck_size)]) for index in range(0, 30)]
                self.decks.append(hsgame.game_objects.Deck(cards, CHARACTER_CLASS.from_str(args[0])))

            elif action == 'keep':
                if len(self.keeps) > 1:
                    raise ReplayException("Maximum of two keep directives per file")
                self.keeps.append(args)

