from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, validator, constr, condecimal
from decimal import Decimal
import stripe
import os
from dotenv import load_dotenv
from typing import Optional, Dict
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
API_KEY = os.getenv("API_KEY")

api_key_header = APIKeyHeader(name="X-API-Key")

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize blockchain and wallet for both networks
mainnet = RootChain(network="mainnet")
testnet = RootChain(network="testnet")

class NetworkModel(BaseModel):
    network: str

    @validator('network')
    def validate_network(cls, v):
        if v not in ['mainnet', 'testnet']:
            raise ValueError("Network must be either 'mainnet' or 'testnet'")
        return v

class WalletCreate(NetworkModel):
    pass

class WalletRecover(NetworkModel):
    mnemonic: constr(min_length=24, max_length=500)  # type: ignore # Validate mnemonic length

class PaymentIntent(NetworkModel):
    amount: condecimal(gt=Decimal('0'))  # type: ignore # Must be positive

class TransferRequest(BaseModel):
    from_address: constr(min_length=30, max_length=50)  # type: ignore # Validate address length
    to_address: constr(min_length=30, max_length=50) # type: ignore
    amount: condecimal(gt=Decimal('0'))  # type: ignore # Must be positive
    private_key: str

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

@app.post("/api/wallet/create", 
    response_model=Dict,
    description="Create a new wallet for the specified network",
    responses={
        200: {
            "description": "Successfully created wallet",
            "content": {
                "application/json": {
                    "example": {
                        "address": "rtc_1234567890abcdef",
                        "private_key": "0x...",
                        "mnemonic": "word1 word2 ...",
                        "balance": "0",
                        "network": "mainnet",
                        "symbol": "ROOT"
                    }
                }
            }
        },
        403: {"description": "Invalid API key"},
        429: {"description": "Rate limit exceeded"}
    }
)
async def create_wallet(
    wallet_data: WalletCreate,
    request: Request,
    api_key: str = Depends(api_key_header)
):
    start_time = time.time()
    try:
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from {request.client.host}")
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        await check_rate_limit(request)
        
        logger.info(f"Creating wallet for network: {wallet_data.network}")
        wallet = RootWallet(network=wallet_data.network)
        wallet_info = wallet.create_wallet()
        
        chain = mainnet if wallet_data.network == "mainnet" else testnet
        balance = get_cached_balance(chain, wallet_info["address"])
        
        response = {
            **wallet_info,
            "balance": balance,
            "network": wallet_data.network,
            "symbol": "ROOT" if wallet_data.network == "mainnet" else "tROOT"
        }
        
        logger.info(f"Successfully created wallet: {wallet_info['address']}")
        return response
    except Exception as e:
        logger.error(f"Error creating wallet: {str(e)}", exc_info=True)
        raise
    finally:
        REQUEST_COUNT.labels(
            endpoint='/api/wallet/create',
            method='POST',
            status='success' if 'response' in locals() else 'error'
        ).inc()
        REQUEST_LATENCY.labels(
            endpoint='/api/wallet/create'
        ).observe(time.time() - start_time)

@app.post("/api/wallet/recover")
async def recover_wallet(wallet_data: WalletRecover):
    try:
        # Recover wallet for specified network
        wallet = RootWallet(network=wallet_data.network)
        wallet_info = wallet.recover_wallet(wallet_data.mnemonic)
        
        # Get balance from appropriate chain
        chain = mainnet if wallet_data.network == "mainnet" else testnet
        balance = chain.get_balance(wallet_info["address"])
        
        return {
            **wallet_info,
            "balance": balance,
            "network": wallet_data.network,
            "symbol": "ROOT" if wallet_data.network == "mainnet" else "tROOT"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/{address}")
async def get_wallet_details(address: str):
    try:
        # Determine network from address prefix
        network = "mainnet" if address.startswith("rtc") else "testnet"
        chain = mainnet if network == "mainnet" else testnet
        
        if not RootWallet.verify_address(address):
            raise HTTPException(status_code=400, detail="Invalid address")
        
        balance = chain.get_balance(address)
        transactions = []
        
        # Get transaction history
        for block in chain.chain:
            for tx in block.transactions:
                if tx["sender"] == address or tx["recipient"] == address:
                    transactions.append({
                        **tx,
                        "block_number": block.index,
                        "timestamp": block.timestamp
                    })
        
        return {
            "address": address,
            "balance": balance,
            "network": network,
            "symbol": "ROOT" if network == "mainnet" else "tROOT",
            "transactions": transactions[-50:]  # Return last 50 transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transfer")
async def transfer_tokens(
    transfer: TransferRequest,
    request: Request,
    api_key: str = Depends(api_key_header)
):
    start_time = time.time()
    try:
        if api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from {request.client.host}")
            raise HTTPException(status_code=403, detail="Invalid API key")
        
        await check_rate_limit(request)
        
        network = "mainnet" if transfer.from_address.startswith("rtc") else "testnet"
        chain = mainnet if network == "mainnet" else testnet
        wallet = RootWallet(network=network)
        
        logger.info(f"Processing transfer from {transfer.from_address} to {transfer.to_address}")
        
        gas_price = get_cached_gas_price(chain)
        gas_limit = 21000
        fee = Decimal(str(gas_price * gas_limit))
        
        balance = get_cached_balance(chain, transfer.from_address)
        if balance < transfer.amount + fee:
            logger.warning(f"Insufficient balance for transfer: {transfer.from_address}")
            raise HTTPException(status_code=400, detail="Insufficient balance including gas fee")
        
        tx = wallet.create_transaction(
            transfer.from_address,
            transfer.to_address,
            transfer.amount,
            transfer.private_key,
            gas_price=gas_price,
            gas_limit=gas_limit
        )
        
        chain.add_transaction(tx)
        
        logger.info(f"Transfer successful: {tx['hash']}")
        return TransactionResponse(
            status="success",
            transaction=tx,
            network=network,
            gas_used=Decimal(str(gas_limit)),
            fee=fee
        )
    except Exception as e:
        logger.error(f"Error processing transfer: {str(e)}", exc_info=True)
        raise
    finally:
        REQUEST_COUNT.labels(
            endpoint='/api/transfer',
            method='POST',
            status='success' if 'tx' in locals() else 'error'
        ).inc()
        REQUEST_LATENCY.labels(
            endpoint='/api/transfer'
        ).observe(time.time() - start_time)

@app.post("/api/payment/create-intent")
async def create_payment_intent(payment: PaymentIntent):
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),  # Convert to cents
            currency="usd",
            metadata={
                "product": "ROOT_TOKEN",
                "network": payment.network
            }
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
            metadata = payment_intent.metadata
            network = metadata.get("network", "mainnet")
            
            # Select appropriate chain and treasury address
            chain = mainnet if network == "mainnet" else testnet
            treasury = "rtc_treasury" if network == "mainnet" else "trtc_treasury"
            
            # Process the successful payment
            amount_tokens = payment_intent.amount / 9000  # $90 = 1 ROOT/tROOT
            recipient_address = metadata.get("recipient_address")
            
            if recipient_address:
                chain.add_transaction({
                    "sender": treasury,
                    "recipient": recipient_address,
                    "amount": amount_tokens,
                    "timestamp": int(time.time())
                })
                
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 