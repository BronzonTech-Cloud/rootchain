from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, validator, constr, condecimal, Field
from decimal import Decimal
import stripe
import os
from dotenv import load_dotenv
from typing import Optional, Dict, List
import sys
import time
from datetime import datetime, timedelta
import logging
from functools import lru_cache
from prometheus_client import Counter, Histogram, start_http_server
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration # type: ignore
sys.path.append('../')
from blockchain.wallet.wallet import RootWallet
from blockchain.core.blockchain import RootChain
from blockchain.wallet.symbols import ROOT, ROOT_TESTNET
from cache_utils import TTLCache
from fastapi.responses import RedirectResponse, JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wallet.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT", "development")
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'wallet_request_count',
    'Number of requests received',
    ['endpoint', 'method', 'status']
)
REQUEST_LATENCY = Histogram(
    'wallet_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

# Start Prometheus metrics server
start_http_server(8001)

load_dotenv()

app = FastAPI(
    title="RootChain Wallet API",
    description="API for managing RootChain wallets and transactions",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
API_KEY = os.getenv("API_KEY", "YJMiJqoKKSpVvzAilQ9AIB5z0UYge1YmQqqDEU1a_KM")  # Default development key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limiting
request_counts: Dict[str, list] = {}
RATE_LIMIT = 100  # requests per minute

async def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    if client_ip not in request_counts:
        request_counts[client_ip] = []
    
    # Remove old requests
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < 60]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[client_ip].append(now)

# CORS middleware
origins = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize blockchain and wallet for both networks
mainnet = RootChain(network="mainnet")
testnet = RootChain(network="testnet")

# Templates
templates = Jinja2Templates(directory="templates")

class NetworkModel(BaseModel):
    network: str

    @validator('network')
    def validate_network(cls, v):
        if v.lower() not in ['mainnet', 'testnet']:
            raise ValueError("Network must be either 'mainnet' or 'testnet'")
        return v.lower()

class WalletCreate(NetworkModel):
    pass

class WalletRecover(NetworkModel):
    mnemonic: constr(min_length=24, max_length=500)  # type: ignore # Validate mnemonic length

class PaymentIntent(NetworkModel):
    amount: condecimal(gt=Decimal('0'))  # type: ignore # Must be positive
    wallet_address: str = Field(..., min_length=30, max_length=50)

    @validator('wallet_address')
    def validate_wallet_address(cls, v, values):
        network = values.get('network', 'mainnet')
        expected_prefix = 'rtc_' if network == 'mainnet' else 'trtc'
        if not v.startswith(expected_prefix):
            raise ValueError(f"Invalid wallet address for {network} network")
        return v

class TransferRequest(BaseModel):
    from_address: constr(min_length=30, max_length=50)  # type: ignore # Validate address length
    to_address: constr(min_length=30, max_length=50) # type: ignore
    amount: condecimal(gt=Decimal('0'))  # type: ignore # Must be positive
    private_key: str
    network: str

    @validator('network')
    def validate_network(cls, v):
        if v.lower() not in ['mainnet', 'testnet']:
            raise ValueError("Network must be either 'mainnet' or 'testnet'")
        return v.lower()

    @validator('to_address')
    def validate_addresses(cls, v, values):
        if 'from_address' in values:
            from_prefix = values['from_address'][:4]
            to_prefix = v[:4]
            if (from_prefix == 'rtc_' and to_prefix != 'rtc_') or \
               (from_prefix == 'trtc' and to_prefix != 'trtc'):
                raise ValueError("Cannot transfer between different networks")
        return v

class TransactionResponse(BaseModel):
    status: str
    transaction: Dict
    network: str
    gas_used: Decimal
    fee: Decimal

# Cache decorators
@TTLCache(maxsize=1000, ttl=60)  # Cache for 60 seconds
def get_cached_balance(chain: RootChain, address: str) -> Decimal:
    return chain.get_balance(address)

@TTLCache(maxsize=1, ttl=10)  # Cache for 10 seconds
def get_cached_gas_price(chain: RootChain) -> Decimal:
    return chain.get_gas_price()

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key:
        return None  # Allow requests without API key in development
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

@app.post("/api/wallet/create")
async def create_wallet(
    request: WalletCreate,
    req: Request,
    api_key: str = Depends(verify_api_key)
):
    await check_rate_limit(req)
    try:
        wallet = RootWallet(network=request.network)
        wallet_info = wallet.create_wallet()  # Get wallet info using create_wallet method
        
        logger.info(f"Created new wallet on {request.network}")
        return {
            "address": wallet_info["address"],
            "private_key": wallet_info["private_key"],
            "mnemonic": wallet_info["mnemonic"],
            "network": request.network,
            "symbol": ROOT_TESTNET if request.network == 'testnet' else ROOT,
            "balance": 0.0
        }
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/recover")
async def recover_wallet(
    request: WalletRecover,
    req: Request,
    api_key: str = Depends(verify_api_key)
):
    await check_rate_limit(req)
    try:
        # Create wallet instance first
        wallet = RootWallet(network=request.network)
        # Then recover using the mnemonic
        wallet_info = wallet.recover_wallet(request.mnemonic)
        
        chain = testnet if request.network == 'testnet' else mainnet
        balance = get_cached_balance(chain, wallet_info["address"])
        
        return {
            "address": wallet_info["address"],
            "private_key": wallet_info["private_key"],
            "mnemonic": request.mnemonic,
            "network": request.network,
            "symbol": ROOT_TESTNET if request.network == 'testnet' else ROOT,
            "balance": float(balance)
        }
    except Exception as e:
        logger.error(f"Error recovering wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/{address}")
async def get_wallet_info(
    address: str,
    req: Request,
    api_key: str = Depends(verify_api_key),
    network: str = 'mainnet'
):
    await check_rate_limit(req)
    try:
        chain = testnet if network == 'testnet' else mainnet
        balance = get_cached_balance(chain, address)
        transactions = chain.get_transactions(address)
        
        formatted_transactions = []
        for tx in transactions:
            tx_type = 'receive' if tx['recipient'] == address else 'send'
            formatted_transactions.append({
                "type": tx_type,
                "amount": float(tx['amount']),
                "timestamp": tx['timestamp'],
                "sender": tx['sender'],
                "recipient": tx['recipient']
            })
        
        return {
            "address": address,
            "balance": float(balance),
            "symbol": ROOT_TESTNET if network == 'testnet' else ROOT,
            "transactions": formatted_transactions
        }
    except Exception as e:
        logger.error(f"Error getting wallet info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transfer")
async def transfer_tokens(
    request: TransferRequest,
    req: Request,
    api_key: str = Depends(verify_api_key)
):
    await check_rate_limit(req)
    try:
        chain = testnet if request.network == 'testnet' else mainnet
        wallet = RootWallet.from_private_key(
            request.private_key,
            network_type=request.network
        )
        
        if wallet.address != request.from_address:
            raise HTTPException(status_code=400, detail="Invalid wallet credentials")
        
        balance = get_cached_balance(chain, wallet.address)
        if float(balance) < float(request.amount):
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        gas_price = get_cached_gas_price(chain)
        gas_limit = Decimal('21000')  # Standard transfer gas limit
        fee = gas_price * gas_limit
        
        if float(balance) < float(request.amount) + float(fee):
            raise HTTPException(status_code=400, detail="Insufficient balance to cover transfer amount and gas fee")
        
        tx = {
            "sender": wallet.address,
            "recipient": request.to_address,
            "amount": float(request.amount),
            "timestamp": int(time.time()),
            "gas_price": float(gas_price),
            "gas_limit": float(gas_limit)
        }
        
        chain.add_transaction(tx)
        logger.info(f"Transfer successful: {request.amount} tokens from {wallet.address} to {request.to_address}")
        
        return TransactionResponse(
            status="success",
            transaction=tx,
            network=request.network,
            gas_used=gas_limit,
            fee=fee
        )
    except Exception as e:
        logger.error(f"Error in transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/create-intent")
async def create_payment_intent(payment: PaymentIntent):
    try:
        # Calculate token amount
        token_amount = payment.amount / Decimal('90.0')  # $90 = 1 ROOT/tROOT
        
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),  # Convert to cents
            currency="usd",
            metadata={
                "product": "ROOT_TOKEN",
                "network": payment.network,
                "recipient_address": payment.wallet_address,
                "token_amount": str(token_amount)
            }
        )
        return {
            "clientSecret": intent.client_secret,
            "token_amount": float(token_amount),
            "wallet_address": payment.wallet_address
        }
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
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
            metadata = payment_intent.metadata
            network = metadata.get("network", "mainnet")
            recipient_address = metadata.get("recipient_address")
            token_amount = Decimal(metadata.get("token_amount", "0"))
            
            if not recipient_address:
                logger.error("No recipient address provided in payment metadata")
                raise ValueError("No recipient address provided")
            
            # Select appropriate chain and treasury address
            chain = mainnet if network == "mainnet" else testnet
            treasury = "rtc_treasury" if network == "mainnet" else "trtc_treasury"
            
            # Create and send the transaction
            tx = {
                "sender": treasury,
                "recipient": recipient_address,
                "amount": float(token_amount),
                "timestamp": int(time.time()),
                "type": "ico_purchase"
            }
            
            chain.add_transaction(tx)
            logger.info(f"ICO purchase successful: {token_amount} tokens sent to {recipient_address}")
            
            return {
                "status": "success",
                "transaction": tx
            }
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return RedirectResponse(url="http://localhost:3001")

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return JSONResponse(
        content={
            "status": "ok",
            "timestamp": int(time.time()),
            "version": "1.0.0"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 