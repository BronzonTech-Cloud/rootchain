from typing import List, Dict, Any, Optional
import time
from .block import Block

class RootChain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.difficulty = 4
        self.mining_reward = 50  # ROOT tokens
        self.block_time = 600  # 10 minutes like Bitcoin
        self.total_supply = 1_000_000  # Initial ROOT supply
        self.symbol = "ROOT"
        self.prefix = "rtc"
        self.balances: Dict[str, float] = {}
        
        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis_transaction = {
            "sender": "0x0",
            "recipient": "RootChain_Treasury",
            "amount": self.total_supply,
            "timestamp": time.time(),
            "type": "genesis"
        }
        genesis_block = Block(0, [genesis_transaction], time.time(), "0")
        self.chain.append(genesis_block)
        self.balances["RootChain_Treasury"] = self.total_supply

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        if sender != "0x0":  # Not mining reward
            if self.get_balance(sender) < amount:
                return False
            
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time(),
            "type": "transfer"
        }
        self.pending_transactions.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address: str) -> Block:
        # Add mining reward transaction
        self.add_transaction("0x0", miner_address, self.mining_reward)
        
        block = Block(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.get_latest_block().hash
        )
        
        block.mine_block(self.difficulty)
        self.chain.append(block)
        
        # Process transactions
        for tx in self.pending_transactions:
            if tx["sender"] != "0x0":
                self.balances[tx["sender"]] = self.get_balance(tx["sender"]) - tx["amount"]
            self.balances[tx["recipient"]] = self.get_balance(tx["recipient"]) + tx["amount"]
        
        self.pending_transactions = []
        return block

    def get_balance(self, address: str) -> float:
        return self.balances.get(address, 0)

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
                
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None

    def get_transactions_by_address(self, address: str) -> List[Dict[str, Any]]:
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address or tx["recipient"] == address:
                    transactions.append(tx)
        return transactions 