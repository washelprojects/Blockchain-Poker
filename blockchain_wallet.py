# blockchain_wallet
from block import Block
from socket import *
import pickle


RED = '\033[91m'
RESET = '\033[0m'

class BlockchainWallet:
    """
    Represents a blockchain wallet for managing blocks and data.

    Attributes:
        blockchain: List of blocks in the blockchain.
        mined_signature: Signature required for a block to be considered mined.
    """
    def __init__(self, mining_complexity):
        """
        Initializes a BlockchainWallet object.

        Args:
            mining_complexity (int): Complexity level for mining (number of leading zeros in hash).
        """
        self.blockchain = []  # Initialize an empty blockchain (list of blocks)
        if mining_complexity > 0:
            self.mined_signature = '0' * mining_complexity
        else:
            self.mined_signature = '0'

    def receive_data(self, pickled_data, node_address):
        """
        Receives data and processes it based on the header.

        Args:
            pickled_data (bytes): Data received.
            node_address (tuple): Address of the sending node.

        Returns:
            tuple: A tuple containing node_address and data if applicable, otherwise None.
        """
        # Receive data in the form of a block, blockchain, or message
        headers = {
            b"BLOCK:": len(b"BLOCK:"),
            b"BLOCKCHAIN:": len(b"BLOCKCHAIN:"),
            b"GET_BLOCKCHAIN": len(b"GET_BLOCKCHAIN")
        }

        header_length = None
        for header, length in headers.items():
            if pickled_data.startswith(header):
                header_length = length
                break

        header = pickled_data[:header_length]
        data = pickled_data[header_length:]

        if header == b"BLOCK:":
            block = pickle.loads(data)
            if block.number == len(self.blockchain) + 1:
                if block.hash.startswith(self.mined_signature):
                    if block.previous_hash.startswith(self.mined_signature):
                        self.blockchain.append(block)
                        #print(f"Received a block with the following attribures:\nnumber = {block.number}\nnonce = {block.nonce}\ndata = {block.data}\nprevious_hash = {block.previous_hash}\nhash = {block.hash}")
                        return None
                    else:
                        print(f"{RED}Error: Received block's previous hash starts with {block.previous_hash[:len(self.mined_signature)]}{RESET}")
                        return None
                else:
                    print(f"{RED}Error: block's hash starts with {block.hash[:len(self.mined_signature)]}{RESET}")
                    return None
            elif block.number > len(self.blockchain) + 1:
                print(f"{RED}Error: Expected sequence number {len(self.blockchain)} but received {block.number}{RESET}")
                return (node_address, b"GET_BLOCKCHAIN") # At this point we know we don't have the longest chain anymore so there is a fork
        elif header == b"BLOCKCHAIN":
            self.blockchain = data          
            return None
        elif header == b"GET_BLOCKCHAIN":
            return (node_address, self.blockchain)
        else:
            print("Unknown header received.")

    def print_wallet(self):
        """
        Print the contents of the blockchain wallet.
        """
        for block in self.blockchain:
            print( "\nBlock number = ", block.number)
            print( "Nonce  = ", block.nonce) 
            print( "Data   = ", block.data)
            print( "Previous Hash = ", block.previous_hash, "Cureent Hash = ", block.hash)


