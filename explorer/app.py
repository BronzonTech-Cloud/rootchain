from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
import sys
sys.path.append('../')
from blockchain.core.blockchain import RootChain
from typing import List, Dict, Any
import os

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize both mainnet and testnet blockchains
mainnet = RootChain(network="mainnet")
testnet = RootChain(network="testnet")

def get_chain(network: str = "mainnet") -> RootChain:
    """Get the appropriate blockchain instance"""
    return mainnet if network.lower() == "mainnet" else testnet

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mainnet_info": mainnet.get_network_info(),
        "testnet_info": testnet.get_network_info()
    })

@app.get("/api/blocks/latest")
async def get_latest_blocks(network: str = "mainnet") -> List[Dict[str, Any]]:
    blockchain = get_chain(network)
    blocks = []
    for block in reversed(blockchain.chain[-10:]):  # Get last 10 blocks
        block_data = block.to_dict()
        block_data["size"] = len(str(block_data).encode())  # Rough size estimation
        blocks.append(block_data)
    return blocks

@app.get("/api/transactions/latest")
async def get_latest_transactions(network: str = "mainnet") -> List[Dict[str, Any]]:
    blockchain = get_chain(network)
    transactions = []
    for block in reversed(blockchain.chain[-10:]):
        for tx in reversed(block.transactions):
            transactions.append({
                "hash": tx.get("hash", ""),
                "from": tx["sender"],
                "to": tx["recipient"],
                "amount": tx["amount"],
                "timestamp": tx["timestamp"],
                "network": tx["network"]
            })
            if len(transactions) >= 10:  # Get last 10 transactions
                return transactions
    return transactions

@app.get("/api/stats")
async def get_network_stats(network: str = "mainnet") -> Dict[str, Any]:
    blockchain = get_chain(network)
    return blockchain.get_network_info()

@app.get("/api/block/{block_hash}")
async def get_block(block_hash: str, network: str = "mainnet") -> Dict[str, Any]:
    blockchain = get_chain(network)
    block = blockchain.get_block_by_hash(block_hash)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    block_data = block.to_dict()
    block_data["size"] = len(str(block_data).encode())
    return block_data

@app.get("/api/transaction/{tx_hash}")
async def get_transaction(tx_hash: str, network: str = "mainnet") -> Dict[str, Any]:
    blockchain = get_chain(network)
    for block in blockchain.chain:
        for tx in block.transactions:
            if tx.get("hash") == tx_hash and tx.get("network") == network:
                return {
                    "hash": tx_hash,
                    "block_hash": block.hash,
                    "from": tx["sender"],
                    "to": tx["recipient"],
                    "amount": tx["amount"],
                    "timestamp": tx["timestamp"],
                    "network": tx["network"]
                }
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/api/address/{address}")
async def get_address_info(address: str) -> Dict[str, Any]:
    # Determine network from address prefix
    network = "mainnet" if address.startswith("rtc") else "testnet"
    blockchain = get_chain(network)
    
    if not blockchain.prefix in address:
        raise HTTPException(status_code=400, detail="Invalid address format")
    
    balance = blockchain.get_balance(address)
    transactions = blockchain.get_transactions_by_address(address)
    
    return {
        "address": address,
        "balance": balance,
        "transactions": transactions,
        "network": network
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port from wallet service 