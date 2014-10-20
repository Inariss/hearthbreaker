import re
import json

import hearthbreaker
import hearthbreaker.constants
from hearthbreaker.constants import CHARACTER_CLASS
import hearthbreaker.game_objects
import hearthbreaker.cards
import hearthbreaker.game_objects
import hearthbreaker.proxies


class ReplayException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ReplayAction:
    def __init__(self):
        super().__init__()
        self.random_numbers = []

    def play(self, game):
        pass

    @staticmethod
    def from_json(name, random, **json):
        cls = None
        if name == 'play':
            cls = PlayAction
        elif name == 'attack':
            cls = AttackAction
        elif name == 'power':
            cls = PowerAction
        elif name == 'end':
            cls = TurnEndAction
        elif name == 'start':
            cls = TurnStartAction
        elif name == 'concede':
            cls = ConcedeAction

        obj = cls.__new__(cls)
        cls.__from_json__(obj, **json)
        obj.random_numbers = []
        for num in random:
            if isinstance(num, dict):
                obj.random_numbers.append(hearthbreaker.proxies.ProxyCharacter.from_json(**num))
            else:
                obj.random_numbers.append(num)
        return obj

    def __to_json__(self):
        pass


class PlayAction(ReplayAction):
    def __init__(self, card, index, target=None):
        super().__init__()
        self.card = card
        self.index = index
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def to_output_string(self):
        if self.target is not None:
            return 'summon({0},{1},{2})'.format(self.card.to_output(), self.index, self.target.to_output())
        return 'summon({0},{1})'.format(self.card.to_output(), self.index)

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)

        game.current_player.agent.next_index = self.index
        game.play_card(self.card.resolve(game))
        game.current_player.agent.nextIndex = -1

    def __to_json__(self):
        if self.target is not None:
            if self.index > -1:
                return {
                    'name': 'play',
                    'card': self.card,
                    'index': self.index,
                    'target': self.target,
                    'random': self.random_numbers,
                }
            else:
                return {
                    'name': 'play',
                    'card': self.card,
                    'target': self.target,
                    'random': self.random_numbers,
                }
        else:
            if self.index > -1:
                return {
                    'name': 'play',
                    'card': self.card,
                    'index': self.index,
                    'random': self.random_numbers,
                }
            else:
                return {
                    'name': 'play',
                    'card': self.card,
                    'random': self.random_numbers,
                }

    def __from_json__(self, card, index=-1, target=None):
        self.card = hearthbreaker.proxies.ProxyCard.from_json(**card)
        self.index = index
        if target:
            self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)
        else:
            self.target = None


class SpellAction(ReplayAction):
    def __init__(self, card, target=None):
        super().__init__()
        self.card = card
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)
        game.play_card(self.card.resolve(game))
        game.current_player.agent.next_target = None

    def to_output_string(self):
        if self.target is not None:
            return 'play({0},{1})'.format(self.card.to_output(), self.target.to_output())
        return 'play({0})'.format(self.card.to_output())

    def __to_json__(self):
        if self.target is not None:
            return {
                'name': 'play',
                'card': self.card,
                'target': self.target,
                'random': self.random_numbers,
            }
        else:
            return {
                'name': 'play',
                'card': self.card,
                'random': self.random_numbers,
            }

    def __from_json__(self, card, target=None):
        self.card = hearthbreaker.proxies.ProxyCard(card)
        if target:
            self.target = hearthbreaker.proxies.ProxyCharacter.from_json(target)
        else:
            self.target = None


class MinionAction(ReplayAction):
    def __init__(self, card, index, target=None):
        super().__init__()
        self.card = card
        self.index = index
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def to_output_string(self):
        if self.target is not None:
            return 'summon({0},{1},{2})'.format(self.card.to_output(), self.index, self.target.to_output())
        return 'summon({0},{1})'.format(self.card.to_output(), self.index)

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)

        game.current_player.agent.next_index = self.index
        game.play_card(self.card.resolve(game))
        game.current_player.agent.nextIndex = -1

    def __to_json__(self):
        if self.target is not None:
            return {
                'name': 'play',
                'card': self.card,
                'index': self.index,
                'target': self.target,
                'random': self.random_numbers,
            }
        else:
            return {
                'name': 'play',
                'card': self.card,
                'index': self.index,
                'random': self.random_numbers,
            }

    def __from_json__(self, card, index, target=None):
        self.card = hearthbreaker.proxies.ProxyCard(card)
        self.index = index
        if target:
            self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)


class AttackAction(ReplayAction):
    def __init__(self, character, target):
        super().__init__()
        self.character = hearthbreaker.proxies.ProxyCharacter(character)
        self.target = hearthbreaker.proxies.ProxyCharacter(target)

    def to_output_string(self):
        return 'attack({0},{1})'.format(self.character.to_output(), self.target.to_output())

    def play(self, game):
        game.current_player.agent.next_target = self.target.resolve(game)
        self.character.resolve(game).attack()
        game.current_player.agent.next_target = None

    def __to_json__(self):
        return {
            'name': 'attack',
            'character': self.character,
            'target': self.target,
            'random': self.random_numbers,
        }

    def __from_json__(self, character, target):
        self.character = hearthbreaker.proxies.ProxyCharacter.from_json(**character)
        self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)


class PowerAction(ReplayAction):
    def __init__(self, target=None):
        super().__init__()
        self.target = target
        if target is not None:
            self.target = hearthbreaker.proxies.ProxyCharacter(target)
        else:
            self.target = None

    def to_output_string(self):
        if self.target is not None:
            return 'power({0})'.format(self.target.to_output())
        else:
            return 'power()'

    def play(self, game):
        if self.target is not None:
            game.current_player.agent.next_target = self.target.resolve(game)
        game.current_player.hero.power.use()
        game.current_player.agent.next_target = None

    def __to_json__(self):
        if self.target:
            return {
                'name': 'power',
                'target': self.target,
                'random': self.random_numbers,
            }
        else:
            return {
                'name': 'power',
                'random': self.random_numbers,
            }

    def __from_json__(self, target):
        self.target = hearthbreaker.proxies.ProxyCharacter.from_json(**target)


class TurnEndAction(ReplayAction):
    def __init__(self):
        super().__init__()
        pass

    def to_output_string(self):
        return 'end()'

    def play(self, game):
        pass

    def __to_json__(self):
        return {
            'name': 'end',
            'random': self.random_numbers,
        }

    def __from_json__(self):
        pass


class TurnStartAction(ReplayAction):
    def __init__(self):
        super().__init__()

    def to_output_string(self):
        return 'start()'

    def play(self, game):
        pass

    def __to_json__(self):
        return {
            'name': 'start',
            'random': self.random_numbers,
        }

    def __from_json__(self):
        pass


class ConcedeAction(ReplayAction):
    def __init__(self):
        super().__init__()

    def to_output_string(self):
        return "concede()"

    def play(self, game):
        game.current_player.hero.die(None)
        game.current_player.hero.activate_delayed()

    def __to_json__(self):
        return {
            'name': 'concede',
            'random': self.random_numbers,
        }

    def __from_json__(self):
        pass


class Replay:
    def __init__(self):
        self.actions = []
        self.last_card = None
        self.card_class = None
        self.last_target = None
        self.last_index = None
        self.decks = []
        self.keeps = []
        self.header_random = []

    def save_decks(self, deck1, deck2):
        self.decks = [deck1, deck2]

    def record_random(self, result):
        if len(self.actions) > 0:
            self.actions[-1].random_numbers.append(result)
        else:
            self.header_random.append(result)

    def _save_played_card(self):
        if self.last_card is not None:
            if issubclass(self.card_class, hearthbreaker.game_objects.MinionCard):
                if self.last_card.targetable:
                    self.actions.append(MinionAction(self.last_card, self.last_index, self.last_target))
                    self.last_card = None
                    self.last_index = None
                    self.last_target = None
                else:
                    self.actions.append(MinionAction(self.last_card, self.last_index))
                    self.last_card = None
                    self.last_index = None
            else:
                if self.last_card.targetable:
                    self.actions.append(SpellAction(self.last_card, self.last_target))
                    self.last_card = None
                    self.last_target = None
                else:
                    self.actions.append(SpellAction(self.last_card))
                    self.last_card = None

    def record_card_played(self, card, index):
        self._save_played_card()
        self.last_card = hearthbreaker.proxies.ProxyCard(index)
        self.last_card.targetable = card.targetable
        self.card_class = type(card)

    def record_option_chosen(self, option):
        self.last_card.set_option(option)

    def record_attack(self, attacker, target):
        self._save_played_card()
        self.actions.append(AttackAction(attacker, target))

    def record_power(self):
        self._save_played_card()
        self.actions.append(PowerAction())

    def record_power_target(self, target):
        self.actions[len(self.actions) - 1].target = hearthbreaker.proxies.ProxyCharacter(target)

    def record_kept_index(self, cards, card_index):
        k_arr = []
        for index in range(0, len(cards)):
            if card_index[index]:
                k_arr.append(index)
        self.keeps.append(k_arr)

    def __shorten_deck(self, cards):
        """
        Mostly for testing, this function will check if the deck is made up of a repeating pattern  and if so, shorten
        the output, since the parser will generate the pattern from a shorter sample
        :param cards: The deck of cards to replace
        :return: an array of cards that represents the deck if repeated until 30 cards are found
        """
        for pattern_length in range(1, 15):
            matched = True
            for index in range(pattern_length, 30):
                if not isinstance(cards[index % pattern_length], type(cards[index])):
                    matched = False
                    break
            if matched:
                return cards[0:pattern_length]

    def write_replay(self, file):
        if 'write' not in dir(file):
            writer = open(file, 'w')
        else:
            writer = file

        for deck in self.decks:
            writer.write("deck(")
            writer.write(hearthbreaker.constants.CHARACTER_CLASS.to_str(deck.character_class))
            writer.write(",")
            writer.write(",".join([card.name for card in self.__shorten_deck(deck.cards)]))
            writer.write(")\n")
        found_random = False
        if self.header_random.count(0) == len(self.header_random):
            for action in self.actions:
                if action.random_numbers.count(0) != len(action.random_numbers):
                    found_random = True
                    break
        else:
            found_random = True
        if not found_random:
            writer.write("random()\n")
        else:
            writer.write("random(")
            writer.write(",".join([str(num) for num in self.header_random]))
            writer.write(")\n")

        for keep in self.keeps:
            writer.write("keep(")
            writer.write(",".join([str(k) for k in keep]))
            writer.write(")\n")

        for action in self.actions:
            writer.write(action.to_output_string() + "\n")
            if len(action.random_numbers) > 0:
                writer.write("random(")
                writer.write(",".join([str(num) for num in action.random_numbers]))
                writer.write(")\n")

    def write_replay_json(self, file):
        if 'write' not in dir(file):
            writer = open(file, 'w')
        else:
            writer = file

        header_cards = [{"cards": [card.name for card in self.__shorten_deck(deck.cards)],
                         "class": CHARACTER_CLASS.to_str(deck.character_class)} for deck in self.decks]

        header = {
            'decks': header_cards,
            'keep': self.keeps,
            'random': self.header_random,
        }
        json.dump({'header': header, 'actions': self.actions}, writer, default=lambda o: o.__to_json__(), indent=2)

    def read_replay_json(self, file):
        if 'read' not in dir(file):
            file = open(file, 'r')

        jd = json.load(file)
        self.decks = []
        for deck in jd['header']['decks']:
            deck_size = len(deck['cards'])
            cards = [hearthbreaker.game_objects.card_lookup(deck['cards'][index % deck_size]) for index in range(0, 30)]
            self.decks.append(
                hearthbreaker.game_objects.Deck(cards, CHARACTER_CLASS.from_str(deck['class'])))

        self.header_random = jd['header']['random']
        self.keeps = jd['header']['keep']
        if len(self.keeps) == 0:
            self.keeps = [[0, 1, 2], [0, 1, 2, 3]]
        self.actions = [ReplayAction.from_json(**js) for js in jd['actions']]

    def parse_replay(self, replayfile):

        if 'read' not in dir(replayfile):
            replayfile = open(replayfile, 'r')
        line_pattern = re.compile("\s*(\w*)\s*\(([^)]*)\)\s*(;.*)?$")
        for line in replayfile:
            (action, args) = line_pattern.match(line).group(1, 2)
            args = [arg.strip() for arg in args.split(",")]
            if action == 'play':
                card = args[0]
                if len(args) > 1:
                    target = args[1]
                else:
                    target = None
                self.actions.append(SpellAction(hearthbreaker.proxies.ProxyCard(card), target))

            elif action == 'summon':
                card = args[0]

                index = int(args[1])

                if len(args) > 2:
                    target = args[2]
                else:
                    target = None

                self.actions.append(MinionAction(hearthbreaker.proxies.ProxyCard(card), index, target))
            elif action == 'attack':
                self.actions.append(AttackAction(args[0], args[1]))
            elif action == 'power':
                if len(args) > 0 and args[0] != '':
                    self.actions.append(PowerAction(args[0]))
                else:
                    self.actions.append(PowerAction())
            elif action == 'end':
                self.actions.append(TurnEndAction())
            elif action == 'start':
                self.actions.append(TurnStartAction())
            elif action == 'random':
                if len(self.actions) == 0:
                    if len(args[0]) > 0:
                        for num in args:
                            self.header_random.append(int(num))

                else:
                    for num in args:
                        if num.isdigit():
                            self.actions[-1].random_numbers.append(int(num))
                        else:
                            self.actions[-1].random_numbers.append(hearthbreaker.proxies.ProxyCharacter(num))

            elif action == 'deck':
                if len(self.decks) > 1:
                    raise ReplayException("Maximum of two decks per file")
                deck_size = len(args) - 1
                cards = [hearthbreaker.game_objects.card_lookup(args[1 + index % deck_size]) for index in range(0, 30)]
                self.decks.append(
                    hearthbreaker.game_objects.Deck(cards, hearthbreaker.constants.CHARACTER_CLASS.from_str(args[0])))

            elif action == 'keep':
                if len(self.keeps) > 1:
                    raise ReplayException("Maximum of two keep directives per file")
                self.keeps.append([int(a) for a in args])

            elif action == 'concede':
                self.actions.append(ConcedeAction())
        replayfile.close()
        if len(self.keeps) is 0:
            self.keeps = [[0, 1, 2], [0, 1, 2, 3]]


class RecordingGame(hearthbreaker.game_objects.Game):
    def __init__(self, decks, agents):
        game = self

        class RecordingAgent:
            __slots__ = ['agent']

            def __init__(self, proxied_agent):
                object.__setattr__(self, "agent", proxied_agent)

            def choose_index(self, card, player):
                index = self.agent.choose_index(card, player)
                game.replay.last_index = index
                return index

            def choose_target(self, targets):
                target = self.agent.choose_target(targets)
                game.replay.last_target = target
                return target

            def choose_option(self, *options):
                option = self.agent.choose_option(options)

                game.replay.record_option_chosen(options.index(option))
                return option

            def __getattr__(self, item):
                return self.agent.__getattribute__(item)

            def __setattr__(self, key, value):
                setattr(self.__getattribute__("agent"), key, value)

        self.replay = hearthbreaker.replay.Replay()
        agents = [RecordingAgent(agents[0]), RecordingAgent(agents[1])]

        super().__init__(decks, agents)
        self.__recorded_randoms__ = []

        self.replay.save_decks(*decks)

        self.bind("kept_cards", self.replay.record_kept_index)

        for player in self.players:
            player.bind("used_power", self.replay.record_power)
            player.hero.bind("found_power_target", self.replay.record_power_target)
            player.bind("card_played", self.replay.record_card_played)
            player.bind("attack", self.replay.record_attack)

    def random_choice(self, choice):
        result = super().random_choice(choice)
        if isinstance(result, hearthbreaker.game_objects.Character):
            self.replay.actions[-1].random_numbers[-1] = hearthbreaker.proxies.ProxyCharacter(result)
        return result

    def _generate_random_between(self, lowest, highest):
        result = super()._generate_random_between(lowest, highest)
        self.replay.record_random(result)
        return result

    def _end_turn(self):
        self.replay._save_played_card()
        self.replay.actions.append(TurnEndAction())
        super()._end_turn()

    def _start_turn(self):
        self.replay.actions.append(TurnStartAction())
        super()._start_turn()


class SavedGame(hearthbreaker.game_objects.Game):
    def __init__(self, replay_file):

        replay = Replay()
        replay.read_replay_json(replay_file)

        self.action_index = -1
        game_ref = self
        k_index = 0

        class ReplayAgent:

            def __init__(self):
                self.next_target = None
                self.next_index = -1
                self.next_option = None

            def do_card_check(self, cards):
                nonlocal k_index
                keep_arr = [False] * len(cards)
                for index in replay.keeps[k_index]:
                    keep_arr[int(index)] = True
                k_index += 1
                return keep_arr

            def do_turn(self, player):
                while game_ref.action_index < len(replay.actions) and not player.hero.dead and type(
                        replay.actions[game_ref.action_index]) is not hearthbreaker.replay.TurnEndAction:
                    game_ref.random_index = 0
                    replay.actions[game_ref.action_index].play(game_ref)
                    game_ref.action_index += 1

            def set_game(self, game):
                pass

            def choose_target(self, targets):
                return self.next_target

            def choose_index(self, card, player):
                return self.next_index

            def choose_option(self, *options):
                return options[self.next_option]

        self.replay = replay
        self.random_index = 0
        super().__init__(replay.decks, [ReplayAgent(), ReplayAgent()])

    def _generate_random_between(self, lowest, highest):
        if len(self.replay.header_random) == 0:
            return 0
        else:
            self.random_index += 1
            if self.action_index == -1:
                return self.replay.header_random[self.random_index - 1]
            return self.replay.actions[self.action_index].random_numbers[self.random_index - 1]

    def random_choice(self, choice):
        if isinstance(self.replay.actions[self.action_index].random_numbers[self.random_index],
                      hearthbreaker.proxies.ProxyCharacter):
            result = self.replay.actions[self.action_index].random_numbers[self.random_index].resolve(self)
            self.random_index += 1
            return result
        return super().random_choice(choice)

    def _start_turn(self):
        self.random_index = 0
        super()._start_turn()
        self.action_index += 1

    def _end_turn(self):
        self.random_index = 0
        super()._end_turn()
        self.action_index += 1

    def pre_game(self):
        super().pre_game()
        self.action_index = 0