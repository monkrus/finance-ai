from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IntegrationProviderException(Exception):
    pass

class BaseProvider(ABC):
    """
    Abstract Base Class for all external integration providers.
    No module should know which provider is being used outside of this abstraction.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def provider_type(self) -> str:
        pass

    @abstractmethod
    async def connect(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Establish a connection with the provider and return a connection token or external ID."""
        pass

    @abstractmethod
    async def disconnect(self, external_account_id: str) -> bool:
        """Revoke access or delete the connection."""
        pass

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Verify credentials."""
        pass

    @abstractmethod
    async def refresh(self, external_account_id: str) -> Dict[str, str]:
        """Refresh an expired OAuth token or session."""
        pass

    @abstractmethod
    async def validate(self, external_account_id: str) -> bool:
        """Validate if the connection is still active and healthy."""
        pass

    @abstractmethod
    async def sync(self, external_account_id: str, last_sync_time: str = None) -> Dict[str, Any]:
        """Pull down the latest data (transactions, holdings, balances)."""
        pass

    @abstractmethod
    async def health(self) -> bool:
        """Check the API health of the provider."""
        pass

class BankProvider(BaseProvider):
    provider_type = "bank"

class BrokerProvider(BaseProvider):
    provider_type = "broker"

class AccountingProvider(BaseProvider):
    provider_type = "accounting"

class ImportProvider(BaseProvider):
    provider_type = "import"
    
class ExportProvider(BaseProvider):
    provider_type = "export"
