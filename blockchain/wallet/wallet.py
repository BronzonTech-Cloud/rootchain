from mnemonic import Mnemonic
from hdwallet import HDWallet
from .symbols import ROOT, ROOT_TESTNET, Symbol
from typing import Dict, Any, Tuple
import hashlib
import os

class RootWallet:
    def __init__(self, network: str = "mainnet"):
        """
        Initialize a RootWallet
        
        Args:
            network (str): Either "mainnet" or "testnet"
        """
        self.mnemonic = Mnemonic("english")
        self.network = network.lower()
        self.symbol = ROOT if self.network == "mainnet" else ROOT_TESTNET
        self.address_prefix = "rtc" if self.network == "mainnet" else "trtc"
        
    def create_wallet(self) -> Dict[str, Any]:
        # Generate 24 word mnemonic
        words = self.mnemonic.generate(strength=256)  # 256 bits = 24 words
        
        # Create HDWallet
        hdwallet = HDWallet()
        hdwallet.from_mnemonic(words)
        # Use different derivation paths for mainnet and testnet
        path = f"m/44'/{self.symbol.coin_type}'/0'/0/0"
        hdwallet.from_path(path)
        
        return {
            "address": f"{self.address_prefix}{hdwallet.p2pkh_address()}",
            "private_key": hdwallet.private_key(),
            "mnemonic": words,
            "balance": 0,
            "network": self.network
        }
    
    def recover_wallet(self, mnemonic: str) -> Dict[str, Any]:
        if not self.mnemonic.check(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
            
        hdwallet = HDWallet()
        hdwallet.from_mnemonic(mnemonic)
        # Use different derivation paths for mainnet and testnet
        path = f"m/44'/{self.symbol.coin_type}'/0'/0/0"
        hdwallet.from_path(path)
        
        return {
            "address": f"{self.address_prefix}{hdwallet.p2pkh_address()}",
            "private_key": hdwallet.private_key(),
            "mnemonic": mnemonic,
            "balance": 0,
            "network": self.network
        }
    
    @staticmethod
    def verify_address(address: str) -> bool:
        """Verify if the address is valid for either mainnet or testnet"""
        if not (address.startswith("rtc") or address.startswith("trtc")):
            return False
        # Add more address verification logic here
        return True
    
    @staticmethod
    def get_address_network(address: str) -> str:
        """Get the network type from an address"""
        if address.startswith("rtc"):
            return "mainnet"
        elif address.startswith("trtc"):
            return "testnet"
        raise ValueError("Invalid address format")
    
    @staticmethod
    def sign_transaction(private_key: str, transaction_data: Dict[str, Any]) -> str:
        # Create transaction signature
        message = str(transaction_data).encode()
        signature = hashlib.sha256(message + private_key.encode()).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(signature: str, transaction_data: Dict[str, Any], public_key: str) -> bool:
        # Verify transaction signature
        message = str(transaction_data).encode()
        expected_signature = hashlib.sha256(message + public_key.encode()).hexdigest()
        return signature == expected_signature 