from locust import HttpUser, task, between
import json

class WalletUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    api_key = "test_api_key"  # Replace with test API key
    
    def on_start(self):
        """Create a wallet when user starts"""
        response = self.client.post(
            "/api/wallet/create",
            headers={"X-API-Key": self.api_key},
            json={"network": "testnet"}
        )
        if response.status_code == 200:
            self.wallet = response.json()
        else:
            self.wallet = None
    
    @task(3)
    def get_wallet_details(self):
        """Get wallet details - most common operation"""
        if self.wallet:
            self.client.get(
                f"/api/wallet/{self.wallet['address']}",
                headers={"X-API-Key": self.api_key}
            )
    
    @task(2)
    def create_wallet(self):
        """Create new wallet - medium frequency"""
        self.client.post(
            "/api/wallet/create",
            headers={"X-API-Key": self.api_key},
            json={"network": "testnet"}
        )
    
    @task(1)
    def transfer_tokens(self):
        """Transfer tokens - least common operation"""
        if self.wallet:
            self.client.post(
                "/api/transfer",
                headers={"X-API-Key": self.api_key},
                json={
                    "from_address": self.wallet["address"],
                    "to_address": "trtc_recipient",
                    "amount": "0.1",
                    "private_key": self.wallet["private_key"]
                }
            )

# To run:
# locust -f locustfile.py --host=http://localhost:8000 