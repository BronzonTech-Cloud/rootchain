from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import time

class SmartContract(ABC):
    def __init__(self, contract_address: str, creator: str):
        self.contract_address = contract_address
        self.creator = creator
        self.state: Dict[str, Any] = {}
        self.created_at = time.time()
    
    @abstractmethod
    def execute(self, sender: str, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

class TokenContract(SmartContract):
    def __init__(self, contract_address: str, creator: str, total_supply: float):
        super().__init__(contract_address, creator)
        self.state["total_supply"] = total_supply
        self.state["balances"] = {creator: total_supply}
        self.state["allowed"] = {}  # For token approvals
    
    def execute(self, sender: str, params: Dict[str, Any]) -> Dict[str, Any]:
        action = params.get("action")
        
        if action == "transfer":
            return self._transfer(sender, params["to"], params["amount"])
        elif action == "approve":
            return self._approve(sender, params["spender"], params["amount"])
        elif action == "transfer_from":
            return self._transfer_from(sender, params["from"], params["to"], params["amount"])
        
        raise ValueError("Invalid action")
    
    def _transfer(self, sender: str, to: str, amount: float) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        sender_balance = self.state["balances"].get(sender, 0)
        if sender_balance < amount:
            raise ValueError("Insufficient balance")
        
        self.state["balances"][sender] = sender_balance - amount
        self.state["balances"][to] = self.state["balances"].get(to, 0) + amount
        
        return {
            "success": True,
            "from": sender,
            "to": to,
            "amount": amount
        }
    
    def _approve(self, sender: str, spender: str, amount: float) -> Dict[str, Any]:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        
        if sender not in self.state["allowed"]:
            self.state["allowed"][sender] = {}
        
        self.state["allowed"][sender][spender] = amount
        
        return {
            "success": True,
            "owner": sender,
            "spender": spender,
            "amount": amount
        }
    
    def _transfer_from(self, sender: str, from_address: str, to: str, amount: float) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        allowed = self.state["allowed"].get(from_address, {}).get(sender, 0)
        if allowed < amount:
            raise ValueError("Not enough allowance")
        
        from_balance = self.state["balances"].get(from_address, 0)
        if from_balance < amount:
            raise ValueError("Insufficient balance")
        
        self.state["balances"][from_address] = from_balance - amount
        self.state["balances"][to] = self.state["balances"].get(to, 0) + amount
        self.state["allowed"][from_address][sender] -= amount
        
        return {
            "success": True,
            "from": from_address,
            "to": to,
            "amount": amount,
            "spender": sender
        }

class ICOContract(SmartContract):
    def __init__(self, contract_address: str, creator: str, token_price: float, 
                 total_tokens: float, start_time: float, end_time: float):
        super().__init__(contract_address, creator)
        self.state["token_price"] = token_price
        self.state["total_tokens"] = total_tokens
        self.state["tokens_sold"] = 0
        self.state["start_time"] = start_time
        self.state["end_time"] = end_time
        self.state["participants"] = {}
    
    def execute(self, sender: str, params: Dict[str, Any]) -> Dict[str, Any]:
        current_time = time.time()
        
        if current_time < self.state["start_time"]:
            raise ValueError("ICO has not started yet")
        
        if current_time > self.state["end_time"]:
            raise ValueError("ICO has ended")
        
        amount = params.get("amount", 0)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        tokens_to_buy = amount / self.state["token_price"]
        if self.state["tokens_sold"] + tokens_to_buy > self.state["total_tokens"]:
            raise ValueError("Not enough tokens available")
        
        self.state["tokens_sold"] += tokens_to_buy
        self.state["participants"][sender] = self.state["participants"].get(sender, 0) + tokens_to_buy
        
        return {
            "success": True,
            "buyer": sender,
            "tokens": tokens_to_buy,
            "amount_paid": amount
        }

class SmartContractManager:
    def __init__(self):
        self.contracts: Dict[str, SmartContract] = {}
    
    def deploy_contract(self, contract_type: str, creator: str, params: Dict[str, Any]) -> str:
        contract_address = f"rtc_contract_{len(self.contracts)}"
        
        if contract_type == "token":
            contract = TokenContract(contract_address, creator, params["total_supply"])
        elif contract_type == "ico":
            contract = ICOContract(
                contract_address,
                creator,
                params["token_price"],
                params["total_tokens"],
                params["start_time"],
                params["end_time"]
            )
        else:
            raise ValueError("Invalid contract type")
        
        self.contracts[contract_address] = contract
        return contract_address
    
    def execute_contract(self, contract_address: str, sender: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if contract_address not in self.contracts:
            raise ValueError("Contract not found")
        
        contract = self.contracts[contract_address]
        return contract.execute(sender, params) 