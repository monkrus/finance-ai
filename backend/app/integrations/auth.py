import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.integration import CredentialVault
from app.integrations.providers import IntegrationProviderException

class CredentialManager:
    """
    Manages OAuth tokens, API keys, and secure credentials using symmetric encryption at rest.
    Never stores plaintext credentials.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Ensure secret key is 32 url-safe base64-encoded bytes for Fernet
        # Fallback padding if SECRET_KEY is too short
        key_bytes = settings.SECRET_KEY.encode('utf-8')
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b'*')
        elif len(key_bytes) > 32:
            key_bytes = key_bytes[:32]
            
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, data: Dict[str, str]) -> str:
        """Encrypt JSON dict into a string."""
        json_data = json.dumps(data)
        encrypted_bytes = self.fernet.encrypt(json_data.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt(self, encrypted_string: str) -> Dict[str, str]:
        """Decrypt string back into JSON dict."""
        decrypted_bytes = self.fernet.decrypt(encrypted_string.encode('utf-8'))
        return json.loads(decrypted_bytes.decode('utf-8'))

    async def store_credentials(self, user_id: int, provider_id: int, credentials: Dict[str, str]) -> CredentialVault:
        """Store or update encrypted credentials for a user+provider."""
        encrypted = self.encrypt(credentials)
        
        result = await self.db.execute(
            select(CredentialVault).filter_by(user_id=user_id, provider_id=provider_id)
        )
        vault = result.scalar_one_or_none()
        
        if vault:
            vault.encrypted_credentials = encrypted
        else:
            vault = CredentialVault(
                user_id=user_id,
                provider_id=provider_id,
                encrypted_credentials=encrypted
            )
            self.db.add(vault)
            
        await self.db.commit()
        await self.db.refresh(vault)
        return vault

    async def get_credentials(self, user_id: int, provider_id: int) -> Dict[str, str]:
        """Retrieve and decrypt credentials."""
        result = await self.db.execute(
            select(CredentialVault).filter_by(user_id=user_id, provider_id=provider_id)
        )
        vault = result.scalar_one_or_none()
        
        if not vault:
            raise IntegrationProviderException("Credentials not found")
            
        return self.decrypt(vault.encrypted_credentials)

    async def delete_credentials(self, user_id: int, provider_id: int):
        """Destroy credentials upon disconnect."""
        result = await self.db.execute(
            select(CredentialVault).filter_by(user_id=user_id, provider_id=provider_id)
        )
        vault = result.scalar_one_or_none()
        if vault:
            await self.db.delete(vault)
            await self.db.commit()
