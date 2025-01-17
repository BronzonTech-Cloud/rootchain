from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
sys.path.append('../')
from blockchain.core.blockchain import RootChain
from blockchain.wallet.symbols import ROOT, ROOT_TESTNET

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize both networks
mainnet = RootChain(network="mainnet")
testnet = RootChain(network="testnet")

# Store historical metrics
class MetricsStore:
    def __init__(self, max_history: int = 24):  # 24 hours of history
        self.max_history = max_history
        self.metrics: Dict[str, List[Dict]] = {
            "mainnet": [],
            "testnet": []
        }
    
    def add_metric(self, network: str, metric: Dict):
        metrics = self.metrics[network]
        metrics.append({**metric, "timestamp": time.time()})
        
        # Keep only last max_history entries
        if len(metrics) > self.max_history:
            metrics.pop(0)
    
    def get_metrics(self, network: str) -> List[Dict]:
        return self.metrics[network]

metrics_store = MetricsStore()

def calculate_avg_block_time(chain: RootChain) -> float:
    if len(chain.chain) < 2:
        return 0.0
    
    # Calculate average time between last 10 blocks
    blocks = chain.chain[-10:]
    times = [b.timestamp for b in blocks]
    diffs = [t2 - t1 for t1, t2 in zip(times[:-1], times[1:])]
    return sum(diffs) / len(diffs) if diffs else 0.0

def calculate_avg_tx_per_block(chain: RootChain) -> float:
    if not chain.chain:
        return 0.0
    
    # Calculate average transactions in last 10 blocks
    blocks = chain.chain[-10:]
    tx_counts = [len(b.transactions) for b in blocks]
    return sum(tx_counts) / len(tx_counts)

def check_network_health(chain: RootChain, network: str) -> Dict:
    issues = []
    score = 100

    # Check block production
    avg_block_time = calculate_avg_block_time(chain)
    if avg_block_time > 120:  # More than 2 minutes
        issues.append(f"High block time: {avg_block_time:.1f}s")
        score -= 20
    elif avg_block_time > 60:  # More than 1 minute
        issues.append(f"Elevated block time: {avg_block_time:.1f}s")
        score -= 10

    # Check pending transactions
    pending_count = len(chain.pending_transactions)
    if pending_count > 1000:
        issues.append(f"High pending transactions: {pending_count}")
        score -= 20
    elif pending_count > 500:
        issues.append(f"Elevated pending transactions: {pending_count}")
        score -= 10

    # Check treasury balance
    treasury_balance = chain.get_balance(f"{'trtc' if network == 'testnet' else 'rtc'}_treasury")
    min_balance = 1000000  # 1M tokens
    if treasury_balance < min_balance:
        issues.append(f"Low treasury balance: {treasury_balance:,} {'tROOT' if network == 'testnet' else 'ROOT'}")
        score -= 20

    # Determine status
    status = "healthy" if score >= 90 else "warning" if score >= 70 else "critical"

    return {
        "status": status,
        "score": max(0, score),
        "issues": issues
    }

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })

@app.get("/api/metrics/current")
async def get_current_metrics():
    mainnet_stats = {
        "network": "mainnet",
        "blocks": len(mainnet.chain),
        "transactions": sum(len(block.transactions) for block in mainnet.chain),
        "pending_transactions": len(mainnet.pending_transactions),
        "total_supply": mainnet.total_supply,
        "treasury_balance": mainnet.get_balance("rtc_treasury"),
        "active_addresses": len(set(
            tx["sender"] for block in mainnet.chain 
            for tx in block.transactions
        ) | set(
            tx["recipient"] for block in mainnet.chain 
            for tx in block.transactions
        )),
        "avg_block_time": calculate_avg_block_time(mainnet),
        "avg_transactions_per_block": calculate_avg_tx_per_block(mainnet),
        "mining_difficulty": mainnet.difficulty,
        "mining_reward": mainnet.mining_reward,
        "last_block_timestamp": mainnet.chain[-1].timestamp if mainnet.chain else 0
    }
    
    testnet_stats = {
        "network": "testnet",
        "blocks": len(testnet.chain),
        "transactions": sum(len(block.transactions) for block in testnet.chain),
        "pending_transactions": len(testnet.pending_transactions),
        "total_supply": testnet.total_supply,
        "treasury_balance": testnet.get_balance("trtc_treasury"),
        "active_addresses": len(set(
            tx["sender"] for block in testnet.chain 
            for tx in block.transactions
        ) | set(
            tx["recipient"] for block in testnet.chain 
            for tx in block.transactions
        )),
        "avg_block_time": calculate_avg_block_time(testnet),
        "avg_transactions_per_block": calculate_avg_tx_per_block(testnet),
        "mining_difficulty": testnet.difficulty,
        "mining_reward": testnet.mining_reward,
        "last_block_timestamp": testnet.chain[-1].timestamp if testnet.chain else 0
    }

    # Calculate comparison metrics
    comparison = {
        "block_height_diff": abs(mainnet_stats["blocks"] - testnet_stats["blocks"]),
        "transaction_volume_ratio": testnet_stats["transactions"] / mainnet_stats["transactions"] if mainnet_stats["transactions"] > 0 else 0,
        "active_addresses_ratio": testnet_stats["active_addresses"] / mainnet_stats["active_addresses"] if mainnet_stats["active_addresses"] > 0 else 0,
        "block_time_ratio": testnet_stats["avg_block_time"] / mainnet_stats["avg_block_time"] if mainnet_stats["avg_block_time"] > 0 else 0
    }

    # Store metrics for history
    metrics_store.add_metric("mainnet", mainnet_stats)
    metrics_store.add_metric("testnet", testnet_stats)

    return {
        "mainnet": mainnet_stats,
        "testnet": testnet_stats,
        "comparison": comparison
    }

@app.get("/api/metrics/history")
async def get_metrics_history(network: str):
    if network not in ["mainnet", "testnet"]:
        raise HTTPException(status_code=400, detail="Invalid network")
    return metrics_store.get_metrics(network)

@app.get("/api/metrics/network-health")
async def get_network_health():
    return {
        "mainnet": check_network_health(mainnet, "mainnet"),
        "testnet": check_network_health(testnet, "testnet")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 