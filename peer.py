
# peer_to_peer_network

import threading
from poker_player import Poker_Player
from tracker import Tracker
from block import Block
from socket import *
from blockchain_wallet import BlockchainWallet
import pickle
import time
import sys


class Peer:
    """
    Represents a peer in a peer-to-peer network for a poker game.

    Attributes:
        player (Poker_Player): Player associated with this peer.
        node_socket (socket): Socket for communication with other peers.
        port (int): Port number of the peer's socket.
        tracker_address (tuple): Address of the tracker server.
        blockchain_wallet (BlockchainWallet): Wallet for managing blockchain.
        connections (list): List of peer connections.
        playerlist (list): List of players in the network.
        new_player (bool): Flag indicating if a new player joined.
        in_progess (int): Flag indicating if a round is in progress.
    """
    def __init__(self, tracker_address, tracker_port):
        """
        Initialize a Peer object.

        Args:
            tracker_address (str): IP address of the tracker server.
            tracker_port (int): Port number of the tracker server.
        """
        self.player = Poker_Player()
        self.node_socket = socket(AF_INET, SOCK_DGRAM)
        self.port = self.node_socket.getsockname()[1]
        self.tracker_address = (tracker_address, tracker_port)
        self.blockchain_wallet = BlockchainWallet(mining_complexity=2)
        self.connections = []
        self.playerlist = []
        self.new_player = False
        self.in_progess = 0
        self.node_socket.settimeout(5)
      
    def connect(self):
        """
        Connect to the tracker server and other peers.
        """
        header = 'HELLO'
        message = (header, self.player.player_name)
        self.node_socket.sendto(pickle.dumps(message), self.tracker_address)
        data, _ = self.node_socket.recvfrom(1024)
        deserialized_data = pickle.loads(data)
        self.connections.clear()
        self.playerlist.clear()
        for entry in deserialized_data[1]:
            self.playerlist.append(entry[1])
            if entry[0][1] != self.node_socket.getsockname()[1]:
                self.connections.append((entry[0][0], entry[0][1]))
        
        message = ("I need blockchain")
        self.broadcast_to_peers('CONNECT', message)

    def ping_tracker(self, tracker_address, node_socket):
        """
        Periodically ping the tracker server to indicate alive status.

        Args:
            tracker_address (tuple): Address of the tracker server.
            node_socket (socket): Socket for communication with the tracker server.
        """
        while not exit_event.is_set():
            message = pickle.dumps(b'ALIVE')
            node_socket.sendto(message, tracker_address)
            time.sleep(0.5)

    def broadcast_to_peers(self, header, payload):
        """
        Broadcast a message to all connected peers.

        Args:
            header (str): Header of the message.
            payload (str): Payload of the message.
        """
        # print("broadcasting")
        for addr in self.connections:
            # print("entry :", addr)
            message_to_peers = (header, payload)
            pickled_payload = pickle.dumps(message_to_peers) 
            self.node_socket.sendto(pickled_payload, addr)

    def receive_from_peers(self):
        """
        Receive messages from connected peers.
        """
        # print("recieving")
        while not exit_event.is_set():
            try:
                data, addr = self.node_socket.recvfrom(1024)
                decoded_data = pickle.loads(data)
                # print(f"Decoded Data: {decoded_data}")
                header = decoded_data[0]
                payload = decoded_data[1]
        
                if header == 'TRACKER': #up-to-date list from tracker
                    #print("recieved from tracker")
                    self.connections.clear()
                    self.playerlist.clear()
                    for entry in payload:
                        self.playerlist.append(entry[1])
                        if entry[0][1] != self.node_socket.getsockname()[1]:
                            self.connections.append((entry[0][0], entry[0][1]))
                    #print("list :", self.playerlist)

                if header == 'CONNECT':
                    self.new_player = True

                if header == 'BLOCKCHAIN':
                    if len(self.blockchain_wallet.blockchain) == 0:
                        self.blockchain_wallet.blockchain = payload
                        #print("blockchain received")

                if header == 'PEER':
                    # print(payload)
                    chain = self.blockchain_wallet.receive_data(payload, ((self.node_socket.getsockname()[0], self.node_socket.getsockname()[1])))
                    # print("message to wallet : ", payload[0])
                    # print("sending to : ", addr)
                    if payload[0] == b'GET_BLOCKCHAIN':
                        pickled_payload = pickle.dumps(chain) 
                        self.broadcast_to_peers('BET', pickled_payload)
                        
                if header == 'BET':
                    print(("recieved bet: "), payload)
                    self.player.round_1.append(payload)

                if header == 'DONE':
                    self.player.round_1_done.append(payload)

                if header == 'REPLAY':
                    self.player.replay_queue.append(payload)

            except:
                pass

    def round_of_poker(self):
        """
        Conduct a round of poker.
        """
        print("New round")

        self.player.round_1.clear()
        self.player.round_1_done.clear()
        self.player.replay_queue.clear()

        print("Game history: ")
        self.blockchain_wallet.print_wallet()


        if self.new_player == True:
            self.broadcast_to_peers('BLOCKCHAIN', self.blockchain_wallet.blockchain)
            self.new_player = False

        if len(self.connections) < 1:
            print("Waiting for more players...")
            while len(self.connections) < 1:
                pass
        bet = self.player.place_bet()
        # print(f"PASSED BET: {bet}")
        bet_touple = (self.player.player_name, bet)
        # print(f"BET TOUPLE: {bet_touple}")
        self.player.round_1.append(bet_touple)
        self.broadcast_to_peers('BET', bet_touple)
        
        while len(self.player.round_1) < len(self.playerlist):
            time.sleep(1.0)
            pass
        self.in_progess = 1
        print("All players have bet this round. Bets: \n",  self.player.round_1)

        win =  self.player.did_you_win()
        self.broadcast_to_peers('DONE', win)

        while len(self.player.round_1_done) < len(self.connections):
            pass

        if win == 'y':
            self.winner()
        elif 'y' not in self.player.round_1_done:
            self.player.money += int(bet)
        else:
            self.player.loss += 1


        print("End of round")
        print("You now have $", self.player.money)

        exit = ''
        while exit != 'y' and exit != 'n':
            exit = input("Would you like to play another round (y/n): ")
        self.broadcast_to_peers('REPLAY', exit)

        while len(self.player.replay_queue) < len(self.connections):
            pass
        if exit == 'n':
            self.node_socket.sendto(pickle.dumps('kill'), (self.node_socket.getsockname()[0],self.node_socket.getsockname()[1]))
            return 1
        else:
            return 0
        
    def winner(self):
        for player in self.playerlist:
            if player == self.player.player_name:
                break
            time.sleep(1.0)

        if len(self.blockchain_wallet.blockchain) == 0:
            prev_hash = "00"
        else:
            prev_hash = self.blockchain_wallet.blockchain[-1].hash

        number_of_winners = 1
        for response in self.player.round_1_done:
            if response == "y":
                number_of_winners += 1

        if number_of_winners > 1:
            for i in range(0, len(self.player.round_1)):
                self.player.round_1[i] = (self.player.round_1[i][0], int(self.player.round_1[i][1]) / number_of_winners)

        self.player.calculate_winnings()



        data_to_add = str(self.player.player_name) + " recieved (from, amount)" + str(self.player.round_1)
        my_block = Block(len(self.blockchain_wallet.blockchain)+1, data_to_add, prev_hash)
        new_block = my_block.mine_block("00")
        self.blockchain_wallet.receive_data(new_block, "127.0.0.1")
        self.broadcast_to_peers('PEER', new_block)




if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) != 3:
        print(f"Invalid Arguments: Call using 'python3 peer.py <tracker address> <tracker port>")
    else:
        try:
            tracker_address = arguments[1]
            tracker_port = int(arguments[2])
            peer = Peer(tracker_address, tracker_port)
            peer.connect()

            exit_event = threading.Event()

            node_thread = threading.Thread(target = peer.ping_tracker, args=(peer.tracker_address, peer.node_socket,))
            node_thread.start()   

            receive_thread = threading.Thread(target = peer.receive_from_peers, args=())
            receive_thread.start()

            while True:
                exit = peer.round_of_poker()
                if exit == 1:
                    exit_event.set()
                    break
                time.sleep(4)

            print("Joining Threads...")
            node_thread.join()
            receive_thread.join()
            print("Joined Threads... Exiting Program")

        except KeyboardInterrupt:
            exit_event.set()
            print("\nJoining Threads...")
            node_thread.join(timeout = 5)
            receive_thread.join(timeout = 5)
            print("Joined Threads... Exiting Program")
