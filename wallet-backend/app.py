from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
from typing import Optional
import sys
sys.path.append('../')
from blockchain.wallet.wallet import RootWallet
from blockchain.core.blockchain import RootChain

load_dotenv()

app = FastAPI()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize blockchain and wallet
blockchain = RootChain()
wallet_manager = RootWallet()

class WalletCreate(BaseModel):
    pass

class WalletRecover(BaseModel):
    mnemonic: str

class PaymentIntent(BaseModel):
    amount: float

@app.post("/api/wallet/create")
async def create_wallet():
    try:
        wallet = wallet_manager.create_wallet()
        return wallet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/recover")
async def recover_wallet(wallet_data: WalletRecover):
    try:
        wallet = wallet_manager.recover_wallet(wallet_data.mnemonic)
        return wallet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/{address}")
async def get_wallet_details(address: str):
    if not wallet_manager.verify_address(address):
        raise HTTPException(status_code=400, detail="Invalid address")
    
    balance = blockchain.get_balance(address)
    return {
        "address": address,
        "balance": balance
    }

@app.post("/api/payment/create-intent")
async def create_payment_intent(payment: PaymentIntent):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),  # Convert to cents
            currency="usd",
            metadata={"product": "ROOT_TOKEN"}
        )
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )
        
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            # Process the successful payment
            # Add ROOT tokens to user's wallet
            amount_root = payment_intent.amount / 9000  # $90 = 1 ROOT
            recipient_address = payment_intent.metadata.get("recipient_address")
            
            if recipient_address:
                blockchain.add_transaction(
                    "RootChain_Treasury",
                    recipient_address,
                    amount_root
                )
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 