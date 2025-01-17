from typing import List, Dict, Any, Optional
import time
from .block import Block

class RootChain:
    def __init__(self, network: str = "mainnet"):
        """
        Initialize RootChain
        
        Args:
            network (str): Either "mainnet" or "testnet"
        """
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self.network = network.lower()
        
        # Network specific configurations
        if self.network == "mainnet":
            self.difficulty = 4
            self.mining_reward = 50  # ROOT tokens
            self.block_time = 600  # 10 minutes like Bitcoin
            self.total_supply = 1_000_000  # Initial ROOT supply
            self.symbol = "ROOT"
            self.prefix = "rtc"
        else:  # testnet
            self.difficulty = 3  # Easier mining on testnet
            self.mining_reward = 100  # More rewards on testnet
            self.block_time = 300  # 5 minutes for faster testing
            self.total_supply = 10_000_000  # More supply on testnet
            self.symbol = "tROOT"
            self.prefix = "trtc"
            
        self.balances: Dict[str, float] = {}
        
        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        treasury_address = f"{self.prefix}_treasury"
        genesis_transaction = {
            "sender": "0x0",
            "recipient": treasury_address,
            "amount": self.total_supply,
            "timestamp": time.time(),
            "type": "genesis",
            "network": self.network
        }
        genesis_block = Block(0, [genesis_transaction], time.time(), "0")
        self.chain.append(genesis_block)
        self.balances[treasury_address] = self.total_supply

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        # Verify addresses match the current network
        if not (sender.startswith(self.prefix) or sender == "0x0") or not recipient.startswith(self.prefix):
            return False
            
        if sender != "0x0":  # Not mining reward
            if self.get_balance(sender) < amount:
                return False
            
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time(),
            "type": "transfer",
            "network": self.network
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
        if not address.startswith(self.prefix):
            return 0.0
        return self.balances.get(address, 0.0)

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

    def get_network(self) -> str:
        return self.network

    def get_network_info(self) -> Dict[str, Any]:
        return {
            "network": self.network,
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "block_time": self.block_time,
            "total_supply": self.total_supply,
            "symbol": self.symbol,
            "prefix": self.prefix,
            "blocks": len(self.chain),
            "pending_transactions": len(self.pending_transactions)
        } 