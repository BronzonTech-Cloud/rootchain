from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Backend API URLs
BACKEND_URL = "http://localhost:8000/api"

class CreateWalletRequest(BaseModel):
    network: str = "mainnet"

class RecoverWalletRequest(BaseModel):
    mnemonic: str
    network: str = "mainnet"

class TransferRequest(BaseModel):
    from_address: str
    to_address: str
    amount: float
    private_key: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "networks": ["mainnet", "testnet"]
    })

@app.post("/api/wallet/create")
async def create_wallet(request: CreateWalletRequest):
    try:
        response = requests.post(f"{BACKEND_URL}/wallet/create", json={"network": request.network})
        return JSONResponse(response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/recover")
async def recover_wallet(request: RecoverWalletRequest):
    try:
        response = requests.post(f"{BACKEND_URL}/wallet/recover", json={
            "mnemonic": request.mnemonic,
            "network": request.network
        })
        return JSONResponse(response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/{address}")
async def get_wallet_details(address: str):
    try:
        # Network is determined from address prefix
        network = "mainnet" if address.startswith("rtc") else "testnet"
        response = requests.get(f"{BACKEND_URL}/wallet/{address}?network={network}")
        return JSONResponse(response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transfer")
async def transfer_tokens(request: TransferRequest):
    try:
        # Validate addresses are on the same network
        from_network = "mainnet" if request.from_address.startswith("rtc") else "testnet"
        to_network = "mainnet" if request.to_address.startswith("rtc") else "testnet"
        
        if from_network != to_network:
            raise HTTPException(
                status_code=400,
                detail="Cannot transfer between different networks"
            )
            
        response = requests.post(f"{BACKEND_URL}/transfer", json={
            "from_address": request.from_address,
            "to_address": request.to_address,
            "amount": request.amount,
            "private_key": request.private_key,
            "network": from_network
        })
        return JSONResponse(response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network/info")
async def get_network_info(network: str = "mainnet"):
    try:
        response = requests.get(f"{BACKEND_URL}/network/info?network={network}")
        return JSONResponse(response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000) 