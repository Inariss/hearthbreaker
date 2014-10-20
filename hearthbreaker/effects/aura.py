import hearthbreaker.effects.base
from hearthbreaker.effects.condition import CardMatches
from hearthbreaker.effects.event import Either, TurnEnded, CardPlayed
from hearthbreaker.effects.action import ManaChange
from hearthbreaker.effects.selector import PlayerSelector


class ManaAura(hearthbreaker.effects.base.AuraUntil):

    def __init__(self, amount, minimum, card_selector, until_played):
        if until_played:
            until = Either(CardPlayed(CardMatches(card_selector)), TurnEnded())
        else:
            until = TurnEnded()
        super().__init__(ManaChange(amount, minimum, card_selector), PlayerSelector(), until)