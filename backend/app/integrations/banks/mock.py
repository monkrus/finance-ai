import uuid
from typing import Dict, Any
from app.integrations.providers import BankProvider, IntegrationProviderException

class MockBankProvider(BankProvider):
    provider_name = "mock_bank"
    
    async def connect(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        if credentials.get("api_key") == "invalid":
            raise IntegrationProviderException("Invalid credentials")
        return {"external_account_id": f"bank_acct_{uuid.uuid4().hex[:8]}"}

    async def disconnect(self, external_account_id: str) -> bool:
        return True

    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        return credentials.get("api_key") != "invalid"

    async def refresh(self, external_account_id: str) -> Dict[str, str]:
        return {"status": "refreshed"}

    async def validate(self, external_account_id: str) -> bool:
        return True

    async def sync(self, external_account_id: str, last_sync_time: str = None) -> Dict[str, Any]:
        # Return mock bank data
        return {
            "balances": {"available": 5000.00, "current": 5200.00, "iso_currency_code": "USD"},
            "transactions": [
                {"transaction_id": "txn_1", "amount": 12.50, "name": "Coffee Shop"},
                {"transaction_id": "txn_2", "amount": -1500.00, "name": "Payroll"}
            ]
        }

    async def health(self) -> bool:
        return True
