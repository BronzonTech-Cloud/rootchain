import hashlib
import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], timestamp: float, previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        # Get network from first transaction (genesis block sets this)
        self.network = transactions[0].get("network", "mainnet") if transactions else "mainnet"
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = (
            str(self.index) +
            str(self.transactions) +
            str(self.timestamp) +
            str(self.previous_hash) +
            str(self.nonce) +
            str(self.network)  # Include network in hash calculation
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "network": self.network
        } 