from block import Block
from blockchain_wallet import BlockchainWallet

if __name__ == "__main__":
    # Test Case Initialization
    blockchain = BlockchainWallet(2)
    from_node = 12345
    to_node = 67890
    amount = 10

    transaction = [from_node, to_node, amount]
    block = Block(1, transaction, previous_hash="00")

    # Block functions test
    print(f"Original Hash: {block.hash}")
    mined_block = block.mine_block("00")
    print(f"Mined Hash: {block.hash}")

    blockchain.ledger[12345] = 100
    blockchain.ledger[67890] = 100
    print(f"Original Blockchain: {blockchain.blockchain}")
    print(f"Original Ledger: {blockchain.ledger}")
    blockchain.receive_data(mined_block, 12345)
    print(f"New Blockchain: {blockchain.blockchain}, Data: {blockchain.blockchain[-1].data}")
    print(f"New Ledger: {blockchain.ledger}")

    # Blockchain Request Test:
    request = b"GET_BLOCKCHAIN"
    response = blockchain.receive_data(request, 12345)
    print(f"{response}")



    