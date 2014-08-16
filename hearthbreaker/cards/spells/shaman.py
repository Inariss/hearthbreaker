import copy
import hearthbreaker.targeting
from hearthbreaker.constants import CHARACTER_CLASS, CARD_RARITY, MINION_TYPE
from hearthbreaker.game_objects import Card, Minion, MinionCard


class AncestralHealing(Card):
    def __init__(self):
        super().__init__("Ancestral Healing", 0, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        # Uses the max health of the minion, so as to combo with Auchenai Soulpriest
        self.target.heal(player.effective_heal_power(self.target.calculate_max_health()), self)
        self.target.taunt = True


class AncestralSpirit(Card):
    def __init__(self):
        super().__init__("Ancestral Spirit", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        def apply_deathrattle(minion):
            def resurrection(*args):
                if old_death_rattle is not None:
                    old_death_rattle(*args)

                minion = self.target.card
                minion.summon(player, game, len(player.minions))

            old_death_rattle = minion.deathrattle
            minion.deathrattle = resurrection

        super().use(player, game)

        apply_deathrattle(self.target)


class Bloodlust(Card):
    def __init__(self):
        super().__init__("Bloodlust", 5, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in player.minions:
            minion.temp_attack += 3


class EarthShock(Card):
    def __init__(self):
        super().__init__("Earth Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.silence()
        self.target.damage(player.effective_spell_damage(1), self)


class FarSight(Card):
    def __init__(self):
        super().__init__("Far Sight", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.EPIC)

    def use(self, player, game):
        class Filter:
            def __init__(self, card):
                self.amount = 3
                self.filter = lambda c: c is card
                self.min = 0

        def reduce_cost(card):
            nonlocal filter
            filter = Filter(card)
            player.unbind("card_drawn", reduce_cost)

        super().use(player, game)

        filter = None
        player.bind("card_drawn", reduce_cost)
        player.draw()
        if filter is not None:
            player.mana_filters.append(filter)


class FeralSpirit(Card):
    def __init__(self):
        super().__init__("Feral Spirit", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=2)

    def use(self, player, game):
        super().use(player, game)

        class SpiritWolf(MinionCard):
            def __init__(self):
                super().__init__("Spirit Wolf", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.SPECIAL)

            def create_minion(self, p):
                minion = Minion(2, 3)
                minion.taunt = True
                return minion

        for i in range(0, 2):
            spirit_wolf = SpiritWolf()
            spirit_wolf.summon(player, game, len(player.minions))


class ForkedLightning(Card):
    def __init__(self):
        super().__init__("Forked Lightning", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON, overload=2)

    def use(self, player, game):
        super().use(player, game)

        targets = copy.copy(game.other_player.minions)
        for i in range(0, 2):
            target = targets.pop(game.random(0, len(targets) - 1))
            target.damage(player.effective_spell_damage(2), self)

    def can_use(self, player, game):
        return super().can_use(player, game) and len(game.other_player.minions) >= 2


class FrostShock(Card):
    def __init__(self):
        super().__init__("Frost Shock", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_enemy_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(1), self)
        self.target.freeze()


class Hex(Card):
    def __init__(self):
        super().__init__("Hex", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        class Frog(MinionCard):
            def __init__(self):
                super().__init__("Frog", 0, CHARACTER_CLASS.ALL, CARD_RARITY.SPECIAL, MINION_TYPE.BEAST)

            def create_minion(self, p):
                return Minion(0, 1, taunt=True)

        frog = Frog()
        minion = frog.create_minion(None)
        minion.card = frog
        self.target.replace(minion)


class LavaBurst(Card):
    def __init__(self):
        super().__init__("Lava Burst", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE,
                         hearthbreaker.targeting.find_spell_target, overload=2)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(5), self)


class LightningBolt(Card):
    def __init__(self):
        super().__init__("Lightning Bolt", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_spell_target, overload=1)

    def use(self, player, game):
        super().use(player, game)

        self.target.damage(player.effective_spell_damage(3), self)


class LightningStorm(Card):
    def __init__(self):
        super().__init__("Lightning Storm", 3, CHARACTER_CLASS.SHAMAN, CARD_RARITY.RARE, overload=2)

    def use(self, player, game):
        super().use(player, game)

        for minion in copy.copy(game.other_player.minions):
            minion.damage(player.effective_spell_damage(game.random(2, 3)), self)


class RockbiterWeapon(Card):
    def __init__(self):
        super().__init__("Rockbiter Weapon", 1, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_friendly_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.change_temp_attack(3)


class TotemicMight(Card):
    def __init__(self):
        super().__init__("Totemic Might", 0, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON)

    def use(self, player, game):
        super().use(player, game)

        for minion in player.minions:
            if minion.card.minion_type == MINION_TYPE.TOTEM:
                minion.increase_health(2)


class Windfury(Card):
    def __init__(self):
        super().__init__("Windfury", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.FREE,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)

        self.target.windfury = True


class Reincarnate(Card):

    def __init__(self):
        super().__init__("Reincarnate", 2, CHARACTER_CLASS.SHAMAN, CARD_RARITY.COMMON,
                         hearthbreaker.targeting.find_minion_spell_target)

    def use(self, player, game):
        super().use(player, game)
        self.target.die(self)
        game.check_delayed()
        self.target.card.summon(self.target.player, game, len(self.target.player.minions))
