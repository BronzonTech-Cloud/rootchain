from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
import sys
sys.path.append('../')
from blockchain.core.blockchain import RootChain
from blockchain.contracts.smart_contract import SmartContractManager, ICOContract
import time

load_dotenv()

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory=".")

# Initialize blockchain and contract manager for both networks
mainnet_chain = RootChain(network="mainnet")
testnet_chain = RootChain(network="testnet")
mainnet_contract_manager = SmartContractManager()
testnet_contract_manager = SmartContractManager()

# Deploy ICO contracts for both networks
def deploy_ico_contract(network: str) -> str:
    chain = mainnet_chain if network == "mainnet" else testnet_chain
    manager = mainnet_contract_manager if network == "mainnet" else testnet_contract_manager
    
    ico_params = {
        "token_price": 90.0 if network == "mainnet" else 45.0,  # Half price on testnet
        "total_tokens": chain.total_supply,
        "start_time": time.time(),
        "end_time": time.time() + (30 * 24 * 60 * 60)  # 30 days duration
    }
    
    treasury_address = f"{chain.prefix}_treasury"
    return manager.deploy_contract(
        "ico",
        treasury_address,
        ico_params
    )

# Deploy contracts for both networks
mainnet_ico_address = deploy_ico_contract("mainnet")
testnet_ico_address = deploy_ico_contract("testnet")

class TokenPurchase(BaseModel):
    amount: float
    network: str = "mainnet"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    mainnet_ico = mainnet_contract_manager.contracts[mainnet_ico_address]
    testnet_ico = testnet_contract_manager.contracts[testnet_ico_address]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mainnet_info": {
            "network": "mainnet",
            "ico_status": get_ico_status("mainnet"),
            "chain_info": mainnet_chain.get_network_info()
        },
        "testnet_info": {
            "network": "testnet",
            "ico_status": get_ico_status("testnet"),
            "chain_info": testnet_chain.get_network_info()
        }
    })

def get_ico_status(network: str) -> dict:
    manager = mainnet_contract_manager if network == "mainnet" else testnet_contract_manager
    address = mainnet_ico_address if network == "mainnet" else testnet_ico_address
    ico_contract = manager.contracts[address]
    
    total_tokens = ico_contract.state["total_tokens"]
    tokens_sold = ico_contract.state["tokens_sold"]
    
    return {
        "total_tokens": total_tokens,
        "tokens_sold": tokens_sold,
        "available_tokens": total_tokens - tokens_sold,
        "token_price": ico_contract.state["token_price"],
        "start_time": ico_contract.state["start_time"],
        "end_time": ico_contract.state["end_time"]
    }

@app.get("/api/ico/status")
async def get_ico_status_api(network: str = "mainnet"):
    return get_ico_status(network)

@app.post("/api/ico/purchase")
async def purchase_tokens(purchase: TokenPurchase):
    if purchase.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Get correct contract and price based on network
    manager = mainnet_contract_manager if purchase.network == "mainnet" else testnet_contract_manager
    address = mainnet_ico_address if purchase.network == "mainnet" else testnet_ico_address
    ico_contract = manager.contracts[address]
    
    total_price = purchase.amount * ico_contract.state["token_price"]
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert to cents
            currency="usd",
            metadata={
                "product": f"ROOT_TOKEN_ICO_{purchase.network.upper()}",
                "amount_tokens": str(purchase.amount),
                "network": purchase.network
            }
        )
        
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ico/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            metadata = payment_intent.metadata
            
            if metadata.get("product", "").startswith("ROOT_TOKEN_ICO"):
                network = metadata.get("network", "mainnet")
                amount_tokens = float(metadata.get("amount_tokens"))
                
                # Execute ICO contract on appropriate network
                manager = mainnet_contract_manager if network == "mainnet" else testnet_contract_manager
                address = mainnet_ico_address if network == "mainnet" else testnet_ico_address
                
                manager.execute_contract(
                    address,
                    metadata.get("recipient_address", "anonymous"),
                    {"amount": payment_intent.amount / 100}  # Convert cents to dollars
                )
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port from other services 