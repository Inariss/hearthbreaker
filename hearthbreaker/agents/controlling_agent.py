from hearthbreaker.agents.basic_agents import Agent


class ControllingAgent(Agent):
    def do_card_check(self, cards):
        return [True, True, True, True]

    def check_opponent_life(self, player):
        print("Health of opponent's hero: {}".format(player.game.other_player.hero.health))

    def attack_with_hero(self, player):
        if player.hero.can_attack():
            print('BEFORE ATTACK WITH HERO')
            self.check_opponent_life(player)
            player.hero.attack()
            self.check_opponent_life(player)
            print('AFTER ATTACK WITH HERO')
        print('HERO CANNOT ATTACK')



    # player atakuje wszystkimi swoimi stronnikami, zaczyna od ataku na other_player.hero
    def attack_opponents_minions_with_my_own_minions(self, player):

        attacking_minions = [minion for minion in player.minions if minion.can_attack()]
        # print("---", attacking_minions, "---")


        attack_done = False
        for minion in attacking_minions:
        # for minion in attacking_minions[:int(len(attacking_minions)/4)]:
            attack_done = True
            print('BEFORE ATTACK WITH MINIONS')
            self.check_opponent_life(player)
            print(">>> Attacking with minion:\n\tlife:", minion)
            minion.attack()
            self.check_opponent_life(player)
            print('AFTER ATTACK WITH MINIONS')
        if not attack_done:
            print('NONE MINION CAN ATTACK')

    def print_info_about_turn(self, player):
        print("--> info -->")
        print("My hero's health:", player.hero.health)
        print("Opponent's health:", player.game.other_player.hero.health)
        print("My current mana:", player.mana)

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

    def play_all_possible_cards_from_hand(self, player):
        '''
        Takes all cards from :param player:'s hand and decides which cards should be played together (maximizing used mana)
        :return:
        '''

        # choose cards that can be played
        print(">>>>>>>>>>>>>>> PLAYING CARDS FROM HAND >>>>>>>>>>>>>>>")
        possible_cards_to_use = [ card for card in player.hand if (card.can_use(player, player.game))]
        print(">>> Possible cards to use: ", possible_cards_to_use)


        # create a list of possible moves (based on mana points)
        all_possible_moves = []
        for j in range(len(possible_cards_to_use)):
            possible_move = []
            mana_left = player.mana
            for i in range(j, len(possible_cards_to_use)):
                card = possible_cards_to_use[i]
                if mana_left > 0 and card.mana <= mana_left:
                    possible_move.append(card)
                    mana_left -= card.mana
            tuple = (possible_move, mana_left)
            all_possible_moves.append(tuple)

        # sort possible moves by used points of mana
        all_possible_moves_sorted_by_mana_left_after_move = sorted(all_possible_moves, key=lambda tuple: tuple[1])

        # print nicely
        print(">>> Possible moves to make (cards, mana_left_aftre_move): ", end=' ')
        if all_possible_moves_sorted_by_mana_left_after_move:
            print("\n>>>    ", end='')
            print(*all_possible_moves_sorted_by_mana_left_after_move, sep='\n>>>    ')
        else:
            print("[]")

        # choose best cards to be played
        cards_to_use = all_possible_moves_sorted_by_mana_left_after_move[0][0] if all_possible_moves_sorted_by_mana_left_after_move else []
        for card in cards_to_use:
            if card.can_use(player, player.game):
                player.game.play_card(card)
                print(">>> Using card from hand:\n>>>    ", card)
        print("<<<<<<<<<<<<<<< END OF PLAYING CARDS FROM HAND <<<<<<<<<<<<<<<")

    def use_hero_power(self, player):
        '''

        :param player:
        :return:
        '''
        if player.hero.power.can_use():
            player.hero.power.use()

    def do_turn(self, player):
        '''

        :param player:
        :return:
        '''
        print("\nSTART A TURN OF CONTROLLING AGENT", player)
        self.print_info_about_turn(player)

        self.play_all_possible_cards_from_hand(player)

        self.attack_opponents_minions_with_my_own_minions(player)
        self.attack_with_hero(player)
        self.use_hero_power(player)
        print("END TURN OF CONTROLLING AGENT",player,"\n")

    def choose_target(self, targets):
        '''

        :param targets:
        :return:
        '''

        print("--- CHOOSING TARGET ---\n--- Choosing target from list:\n---    ", end='')
        print(*targets, sep='\n---    ')

        # >>> ERROR: sometimes both heros are in targets list, making it possible for minion to attack its owner
        if len(targets)>=2 and type(targets[-2])==type(targets[-1]):
            print('='*10, " ERROR ", '='*10, "TYPES", '='*10 ,type(targets[-2]), type(targets[-1]))
        # <<< ERROR

        target_chosen = targets[0]
        print("--- CHOSEN TARGET:\n---    ", target_chosen)

        return target_chosen

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]




