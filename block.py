# block
import hashlib
import pickle

class Block:
    """
    Represents a block in a blockchain.

    Attributes:
        number (int): The position of the block.
        nonce (int): Nonce for mining.
        data (list): List of transactions between peers.
        previous_hash (str): Hash of the previous block.
        hash (str): Hash of the current block (to be calculated).
    """
    def __init__(self, number, transactions, previous_hash):
        
        self.number = number # Position of block
        self.nonce = 0  # Nonce for mining
        # print(f"Data contains: {transactions}")
        self.data = transactions  # Transactions between peers
        self.previous_hash = previous_hash  # Hash of the previous block
        self.hash = None  # Hash of the current block (to be calculated)

    def calculate_hash(self):
        """
        Calculates the hash of the block based on its attributes.
        """
        encoded_block = f"{self.number}{self.nonce}{self.data}{self.previous_hash}{self.hash}".encode()
        self.hash = hashlib.sha256(encoded_block).hexdigest()
    
    def mine_block(self, mined_signature):
        """
        Mines the block until the hash starts with the specified signature.

        Args:
            mined_signature (str): Signature to be matched for mining.

        Returns:
            bytes: The mined block with its header.
        """
        while True:
            self.nonce += 1
            self.calculate_hash()
            if self.hash.startswith(mined_signature):
                block_data = pickle.dumps(self)
                block_with_header = b"BLOCK:" + block_data
                # print("Block mined with hash: ", self.hash)
                return block_with_header
    
