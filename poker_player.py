# poker game
import threading
import sys
from blockchain_wallet import BlockchainWallet

class Poker_Player:
    """
    Represents a poker player.

    Attributes:
        player_name (str): The player's name.
        money (int): The amount of money the player has.
        wins (int): The number of rounds the player has won.
        loss (int): The number of rounds the player has lost.
        ledger (BlockchainWallet): The blockchain wallet for the player.
        round (int): The current round number.
        round_1 (list): A list to store bets made in the first round.
        round_1_done (list): A list to store completed bets from the first round.
        replay_queue (list): A queue for replaying rounds.
    """
    def __init__(self):
        """
        Initializes a Poker_Player object.
        """
        self.player_name = self.create_player()
        #Every player starts off initially with 100 dollars? We can make this an initial input aswell
        self.money = 100
        self.wins = 0
        self.loss = 0
        self.ledger =  BlockchainWallet(mining_complexity=2)
        self.round = 1
        self.round_1 = []
        self.round_1_done = []
        self.replay_queue = []


    def create_player(self):
        """
        Prompts the user for their player name and returns it.

        Returns:
            str: The player's name.
        """
        # Prompt the user for their player name
        player_name = input("Please enter your player name: ")
        print("Hello, " + player_name + "! Welcome to the game.")
        return player_name
    
    def place_bet(self):
        """
        Prompts the player to place a bet.

        Returns:
            int: The amount of the bet.
        """
        bet = input("Please enter amount to bet: \n")
        while True:
            if not bet.isdigit() or int(bet) <= 0 :
                print("Please enter a valid bet.")
                bet = input("Please enter amount to bet: \n")
            elif (self.money-int(bet)) < 0:
                print("Insufficient funds")
                bet = input("Please enter amount to bet: \n")
            else:
                break
        self.money = self.money - int(bet)
        # print(f"THE BET IS: {bet}")
        return bet
            
    def did_you_win(self):
        """
        Prompts the player to indicate whether they won the round.

        Returns:
            str: 'y' if the player won, 'n' otherwise.
        """
        win = ''
        while win != 'y' and win != 'n':
            win = input("Did you win the round? (y/n): \n")
        return win

    def calculate_winnings(self):
        """
        Calculates the player's winnings for the round and updates the player's money.
        """
        self.wins += 1
        total_winnings = 0
        for bets in self.round_1:
            total_winnings = total_winnings + int(bets[1])
        self.money = self.money + total_winnings
        print("You won $", total_winnings)
        
            