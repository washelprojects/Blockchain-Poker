# main.py
from blockchain_wallet import BlockchainWallet
from block import Block
from p2p import PeerToPeerNetwork

def main():
    # Instantiate objects
    wallet = BlockchainWallet()
    block = Block(nonce=123, data="Transaction data", previous_hash="Previous hash")
    network = PeerToPeerNetwork()

    # Perform operations
    wallet.mine_block()
    network.add_peer("peer1")
    network.broadcast_to_peers("Hello from peer1")

if __name__ == "__main__":
    main()