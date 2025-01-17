from typing import Optional

class Symbol:
    def __init__(self, name: str, coin_type: int, symbol: str, network: str, segwit: bool = False):
        self.name = name
        self.coin_type = coin_type
        self.symbol = symbol
        self.network = network
        self.segwit = segwit

# Define ROOT symbols for both mainnet and testnet
ROOT = Symbol(
    name="RootChain",
    coin_type=8888,  # Custom coin type for ROOT mainnet
    symbol="ROOT",
    network="mainnet"
)

ROOT_TESTNET = Symbol(
    name="RootChain Testnet",
    coin_type=8889,  # Different coin type for testnet
    symbol="tROOT",  # Prefix with 't' to indicate testnet
    network="testnet"
) 