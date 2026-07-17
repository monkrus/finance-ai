import uuid
from typing import Dict, Any
from app.integrations.providers import BrokerProvider, IntegrationProviderException

class MockBrokerProvider(BrokerProvider):
    provider_name = "mock_broker"
    
    async def connect(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        if credentials.get("api_key") == "invalid":
            raise IntegrationProviderException("Invalid credentials")
        return {"external_account_id": f"broker_acct_{uuid.uuid4().hex[:8]}"}

    async def disconnect(self, external_account_id: str) -> bool:
        return True

    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        return credentials.get("api_key") != "invalid"

    async def refresh(self, external_account_id: str) -> Dict[str, str]:
        return {"status": "refreshed"}

    async def validate(self, external_account_id: str) -> bool:
        return True

    async def sync(self, external_account_id: str, last_sync_time: str = None) -> Dict[str, Any]:
        # Return mock broker data
        return {
            "balances": {"cash": 12000.50, "iso_currency_code": "USD"},
            "holdings": [
                {"symbol": "AAPL", "quantity": 50, "price": 150.0},
                {"symbol": "MSFT", "quantity": 20, "price": 310.0}
            ]
        }

    async def health(self) -> bool:
        return True
