from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
import sys
import time
from datetime import datetime, timedelta
sys.path.append('../')
from blockchain.core.blockchain import RootChain

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize testnet blockchain
testnet = RootChain(network="testnet")

# Track faucet requests to prevent abuse
faucet_requests = {}  # address -> last_request_time
MAX_TOKENS = 1000  # Maximum tokens per request
COOLDOWN_HOURS = 24  # Hours between requests

class FaucetRequest(BaseModel):
    address: str
    amount: float = MAX_TOKENS

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "max_tokens": MAX_TOKENS,
        "cooldown_hours": COOLDOWN_HOURS
    })

@app.post("/api/request-tokens")
async def request_tokens(request: FaucetRequest):
    # Validate address format
    if not request.address.startswith("trtc"):
        raise HTTPException(
            status_code=400,
            detail="Invalid address format. Must be a testnet address (starts with 'trtc')"
        )
    
    # Validate amount
    if request.amount <= 0 or request.amount > MAX_TOKENS:
        raise HTTPException(
            status_code=400,
            detail=f"Amount must be between 0 and {MAX_TOKENS} tROOT"
        )
    
    # Check cooldown
    last_request = faucet_requests.get(request.address)
    if last_request:
        time_since_last = datetime.now() - last_request
        if time_since_last < timedelta(hours=COOLDOWN_HOURS):
            hours_left = COOLDOWN_HOURS - (time_since_last.total_seconds() / 3600)
            raise HTTPException(
                status_code=400,
                detail=f"Please wait {hours_left:.1f} hours before requesting more tokens"
            )
    
    try:
        # Send tokens from treasury to the requester
        treasury_address = f"{testnet.prefix}_treasury"
        success = testnet.add_transaction(
            sender=treasury_address,
            recipient=request.address,
            amount=request.amount
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send tokens. Treasury might be empty."
            )
        
        # Mine the block to confirm the transaction
        miner_address = "trtc_faucet_miner"
        testnet.mine_pending_transactions(miner_address)
        
        # Update faucet request tracking
        faucet_requests[request.address] = datetime.now()
        
        return {
            "success": True,
            "message": f"Successfully sent {request.amount} tROOT to {request.address}",
            "transaction": {
                "from": treasury_address,
                "to": request.address,
                "amount": request.amount,
                "network": "testnet"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/faucet-info")
async def get_faucet_info():
    treasury_address = f"{testnet.prefix}_treasury"
    return {
        "treasury_balance": testnet.get_balance(treasury_address),
        "max_tokens_per_request": MAX_TOKENS,
        "cooldown_hours": COOLDOWN_HOURS,
        "active_requests": len(faucet_requests),
        "network": "testnet"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 