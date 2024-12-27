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

# Initialize blockchain and contract manager
blockchain = RootChain()
contract_manager = SmartContractManager()

# Deploy ICO contract
ico_params = {
    "token_price": 90.0,  # $90 per ROOT
    "total_tokens": 1_000_000,  # 1 million ROOT tokens
    "start_time": time.time(),  # Start immediately
    "end_time": time.time() + (30 * 24 * 60 * 60)  # 30 days duration
}
ico_contract_address = contract_manager.deploy_contract(
    "ico",
    "RootChain_Treasury",
    ico_params
)

class TokenPurchase(BaseModel):
    amount: float

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/ico/status")
async def get_ico_status():
    ico_contract = contract_manager.contracts[ico_contract_address]
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

@app.post("/api/ico/purchase")
async def purchase_tokens(purchase: TokenPurchase):
    if purchase.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    total_price = purchase.amount * 90  # $90 per ROOT
    
    try:
        # Create Stripe payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),  # Convert to cents
            currency="usd",
            metadata={
                "product": "ROOT_TOKEN_ICO",
                "amount_tokens": str(purchase.amount)
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
            
            if payment_intent.metadata.get("product") == "ROOT_TOKEN_ICO":
                amount_tokens = float(payment_intent.metadata.get("amount_tokens"))
                
                # Execute ICO contract to purchase tokens
                contract_manager.execute_contract(
                    ico_contract_address,
                    payment_intent.metadata.get("recipient_address", "anonymous"),
                    {"amount": payment_intent.amount / 100}  # Convert cents to dollars
                )
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Different port from other services 