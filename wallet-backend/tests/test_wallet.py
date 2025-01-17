import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, mainnet, testnet

client = TestClient(app)

# Mock data
MOCK_API_KEY = "test_api_key"
MOCK_WALLET = {
    "address": "rtc_1234567890abcdef",
    "private_key": "0x123...",
    "mnemonic": "word1 word2 word3 ...",
    "network": "mainnet"
}
MOCK_BALANCE = Decimal("100.0")

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("API_KEY", MOCK_API_KEY)

@pytest.fixture
def mock_chain():
    with patch('blockchain.core.blockchain.RootChain') as mock:
        mock.return_value.get_balance.return_value = MOCK_BALANCE
        mock.return_value.get_gas_price.return_value = Decimal("0.00001")
        yield mock

@pytest.fixture
def mock_wallet():
    with patch('blockchain.wallet.wallet.RootWallet') as mock:
        mock.return_value.create_wallet.return_value = MOCK_WALLET
        mock.return_value.recover_wallet.return_value = MOCK_WALLET
        mock.verify_address.return_value = True
        yield mock

def test_create_wallet_success(mock_env, mock_wallet, mock_chain):
    response = client.post(
        "/api/wallet/create",
        headers={"X-API-Key": MOCK_API_KEY},
        json={"network": "mainnet"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == MOCK_WALLET["address"]
    assert data["network"] == "mainnet"
    assert data["balance"] == str(MOCK_BALANCE)

def test_create_wallet_invalid_api_key(mock_env):
    response = client.post(
        "/api/wallet/create",
        headers={"X-API-Key": "invalid_key"},
        json={"network": "mainnet"}
    )
    assert response.status_code == 403

def test_create_wallet_invalid_network(mock_env, mock_wallet):
    response = client.post(
        "/api/wallet/create",
        headers={"X-API-Key": MOCK_API_KEY},
        json={"network": "invalid"}
    )
    assert response.status_code == 422

def test_recover_wallet_success(mock_env, mock_wallet, mock_chain):
    response = client.post(
        "/api/wallet/recover",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "network": "mainnet",
            "mnemonic": "word1 word2 word3 ..."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == MOCK_WALLET["address"]
    assert data["network"] == "mainnet"

def test_get_wallet_details_success(mock_env, mock_wallet, mock_chain):
    response = client.get(
        f"/api/wallet/{MOCK_WALLET['address']}",
        headers={"X-API-Key": MOCK_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == MOCK_WALLET["address"]
    assert data["balance"] == str(MOCK_BALANCE)

def test_transfer_tokens_success(mock_env, mock_wallet, mock_chain):
    response = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "rtc_recipient",
            "amount": "10.0",
            "private_key": "0x123..."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["network"] == "mainnet"

def test_transfer_tokens_insufficient_balance(mock_env, mock_wallet, mock_chain):
    mock_chain.return_value.get_balance.return_value = Decimal("0.0")
    response = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "rtc_recipient",
            "amount": "10.0",
            "private_key": "0x123..."
        }
    )
    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]

def test_transfer_tokens_cross_network(mock_env, mock_wallet):
    response = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": "rtc_sender",
            "to_address": "trtc_recipient",
            "amount": "10.0",
            "private_key": "0x123..."
        }
    )
    assert response.status_code == 400
    assert "Cannot transfer between different networks" in response.json()["detail"]

# Integration tests
@pytest.mark.integration
def test_full_wallet_workflow():
    # Create wallet
    create_response = client.post(
        "/api/wallet/create",
        headers={"X-API-Key": MOCK_API_KEY},
        json={"network": "testnet"}
    )
    assert create_response.status_code == 200
    wallet_data = create_response.json()
    
    # Get wallet details
    details_response = client.get(
        f"/api/wallet/{wallet_data['address']}",
        headers={"X-API-Key": MOCK_API_KEY}
    )
    assert details_response.status_code == 200
    
    # Attempt transfer
    transfer_response = client.post(
        "/api/transfer",
        headers={"X-API-Key": MOCK_API_KEY},
        json={
            "from_address": wallet_data["address"],
            "to_address": "trtc_recipient",
            "amount": "1.0",
            "private_key": wallet_data["private_key"]
        }
    )
    assert transfer_response.status_code in [200, 400]  # Either success or insufficient balance 