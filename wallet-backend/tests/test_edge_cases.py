import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
import sys
import os
import time
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, mainnet, testnet, RATE_LIMIT

client = TestClient(app)

MOCK_API_KEY = "test_api_key"

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("API_KEY", MOCK_API_KEY)

def test_rate_limit_exceeded(mock_env):
    """Test rate limiting functionality"""
    # Make RATE_LIMIT + 1 requests
    for _ in range(RATE_LIMIT + 1):
        response = client.post(
            "/api/wallet/create",
            headers={"X-API-Key": MOCK_API_KEY},
            json={"network": "testnet"}
        )
        if response.status_code == 429:
            break
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_invalid_mnemonic_length(mock_env):
    """Test mnemonic validation"""
    response = client.post(
        "/api/wallet/recover",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "network": "mainnet",
            "mnemonic": "too short"
        }
    )
    assert response.status_code == 422

def test_negative_transfer_amount(mock_env):
    """Test negative amount validation"""
    response = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "rtc_recipient",
            "amount": "-10.0",
            "private_key": "0x123..."
        }
    )
    assert response.status_code == 422

def test_invalid_address_format(mock_env):
    """Test address format validation"""
    response = client.get(
        "/api/wallet/invalid_address",
        headers={"X-API-Key": MOCK_API_KEY}
    )
    assert response.status_code == 400
    assert "Invalid address" in response.json()["detail"]

@pytest.mark.asyncio
async def test_concurrent_transfers(mock_env, mock_chain):
    """Test concurrent transfer handling"""
    import asyncio
    import httpx
    
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as ac:
        # Create multiple concurrent transfer requests
        tasks = []
        for _ in range(5):
            tasks.append(
                ac.post(
                    "/api/transfer",
                    headers={"X-API-Key": MOCK_API_KEY},
                    json={
                        "from_address": "rtc_sender",
                        "to_address": "rtc_recipient",
                        "amount": "1.0",
                        "private_key": "0x123..."
                    }
                )
            )
        
        responses = await asyncio.gather(*tasks)
        # Check that all requests were processed
        assert all(r.status_code in [200, 400] for r in responses)

def test_cache_invalidation(mock_env, mock_chain):
    """Test balance cache invalidation after transfer"""
    # Get initial balance
    response1 = client.get(
        "/api/wallet/rtc_test",
        headers={"X-API-Key": MOCK_API_KEY}
    )
    initial_balance = Decimal(response1.json()["balance"])
    
    # Make transfer
    client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_test",
            "to_address": "rtc_recipient",
            "amount": "1.0",
            "private_key": "0x123..."
        }
    )
    
    # Get balance again
    response2 = client.get(
        "/api/wallet/rtc_test",
        headers={"X-API-Key": MOCK_API_KEY}
    )
    final_balance = Decimal(response2.json()["balance"])
    
    # Balance should be different
    assert initial_balance != final_balance

def test_gas_price_changes(mock_env, mock_chain):
    """Test gas price updates"""
    mock_chain.return_value.get_gas_price.side_effect = [
        Decimal("0.00001"),
        Decimal("0.00002")
    ]
    
    # Make two transfers
    response1 = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "rtc_recipient",
            "amount": "1.0",
            "private_key": "0x123..."
        }
    )
    
    time.sleep(11)  # Wait for gas price cache to expire
    
    response2 = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "rtc_recipient",
            "amount": "1.0",
            "private_key": "0x123..."
        }
    )
    
    # Gas prices should be different
    fee1 = Decimal(response1.json()["fee"])
    fee2 = Decimal(response2.json()["fee"])
    assert fee1 != fee2

def test_payment_validation():
    """Test payment amount validation"""
    response = client.post(
        "/api/payment/create-intent",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "amount": 0,
            "network": "mainnet"
        }
    )
    assert response.status_code == 422

def test_webhook_signature_validation(mock_env):
    """Test Stripe webhook signature validation"""
    response = client.post(
        "/api/payment/webhook",
        headers={
            "X-API-Key": MOCK_API_KEY,
            "stripe-signature": "invalid_signature"
        },
        json={}
    )
    assert response.status_code == 400 