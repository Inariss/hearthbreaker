from hearthbreaker.agents.basic_agents import Agent

# Agresive
# atakuje
# sprawdza inne mozliwości
# wybrać wszytskie karty ktorymi można zadac obrazenia w tej rundzie
# użyć tej ktora da najwieksze obrazenie
# atakuje albo stronnikiem albo karta 

# 1) najpierw po wszyst. kartach, jakie można użyć, to je użyć
# 2) zaatakować wszystkimi możliwymi stronnikami

class AggressiveAgent(Agent):
    def do_card_check(self, cards):
        return [True, True, True, True]

    def check_opponent_life(self, player):
        print ("Health of opponent's hero: {}".format(player.game.other_player.hero.health))
    
    def attack_with_hero(self,player):
        print('ATTACKING WITH HERO')
        if player.hero.can_attack():
            print('BEFORE ATTACK WITH HERO')
            self.check_opponent_life(player)
            player.hero.attack()
            self.check_opponent_life(player)
            print('AFTER ATTACK WITH HERO')
        print('HERO CANNOT ATTACK')

    # player atakuje wszystkimi swoimi stronnikami, zaczyna od ataku na other_player.hero
    def attack_with_all_possible_minions(self,player):
        attack_done = False
        for minion in player.minions:
            if minion.can_attack():
                print('BEFORE ATTACK WITH MINIONS')
                self.check_opponent_life(player)
                print(">>> Attacking with minion:\n\tlife:", minion)
                minion.attack()
                player.game.attack_target(minion, player.game.other_player.hero)
                attack_done = True
                self.check_opponent_life(player)
                print('AFTER ATTACK WITH MINIONS')
        if not attack_done:
            print('NONE MINION CAN ATTACK')

    # player używa wszystkie karty jakie może użyć, czyli dopóki starczy mu many
    def use_all_possible_cards(self, player):
        print(">>>>>>>>>>>>>>> PLAYING CARDS FROM HAND >>>>>>>>>>>>>>>")
        possible_cards_to_use = [ card for card in player.hand if (card.can_use(player, player.game))]
        print(">>> Possible cards to use: ", possible_cards_to_use)


        card_costs = [card.mana for card in player.hand]
        # print("Card costs: {}".format(card_costs))
        done_something = True
        
        while done_something:
            # print("Current mana: {}".format(player.mana))
            done_something = False
            for card in player.hand:
                if card.can_use(player, player.game):
                    player.game.play_card(card)
                    print(">>> Using card from hand:\n>>>    ", card)
                    # print("used card",card)
                    done_something = True
                    break
        print("<<<<<<<<<<<<<<< END OF PLAYING CARDS FROM HAND <<<<<<<<<<<<<<<")


    # player używa power swojego hero
    def use_hero_power(self, player):
        if player.hero.power.can_use():
                player.hero.power.use()

    def print_info_about_turn(self, player):
        print("--> info -->")
        print("My hero's health:", player.hero.health)
        print("My hero's card:", player.hero.card)
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

    def do_turn(self, player):
        print("\nSTART A TURN OF AGGRESSIVE AGENT", player)
        self.print_info_about_turn(player)
        self.use_all_possible_cards(player)
        self.attack_with_all_possible_minions(player)
        self.attack_with_hero(player)
        self.use_hero_power(player)
        print("END TURN OF AGGRESSIVE AGENT",player,"\n")
           

    def choose_target(self, targets):
        print("--- CHOOSING TARGET ---\n--- Choosing target from list:\n---    ", end='')
        print(*targets, sep='\n---    ')
        if (len(targets)>=2):
            target_chosen = targets[-1]
        else:
            target_chosen = targets[-1]
        print("--- CHOSEN TARGET:\n---    ", target_chosen)
        return target_chosen

    def choose_index(self, card, player):
        return 0

    def choose_option(self, options, player):
        return self.filter_options(options, player)[0]


            

