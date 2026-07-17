import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.integrations.providers import BaseProvider
from app.integrations.banks.mock import MockBankProvider
from app.integrations.brokers.mock import MockBrokerProvider
from app.integrations.auth import CredentialManager
from app.integrations.import_engine import ImportEngine
from app.integrations.export_engine import ExportEngine
from app.integrations.sync import SyncEngine
from app.integrations.audit import AuditLogger

from app.models.integration import IntegrationProvider, ConnectedAccount, SyncJob, ImportJob, ExportJob

logger = logging.getLogger(__name__)

class IntegrationEngine:
    """
    Facade for all external integrations. 
    Strictly isolated entry point. No other module should speak to external providers directly.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth = CredentialManager(db)
        self.importer = ImportEngine(db)
        self.exporter = ExportEngine(db)
        self.sync_engine = SyncEngine(db)
        self.audit = AuditLogger(db)
        
        # Pluggable Provider Registry
        self.providers: Dict[str, BaseProvider] = {
            "mock_bank": MockBankProvider(),
            "mock_broker": MockBrokerProvider()
        }

    def _get_provider(self, name: str) -> BaseProvider:
        if name not in self.providers:
            raise ValueError(f"Provider {name} not found")
        return self.providers[name]

    # --- Provider Connect Lifecycle ---
    async def get_providers(self) -> List[IntegrationProvider]:
        result = await self.db.execute(select(IntegrationProvider).filter_by(is_active=True))
        return list(result.scalars().all())

    async def connect_provider(self, user_id: int, provider_name: str, credentials: Dict[str, str]) -> ConnectedAccount:
        provider = self._get_provider(provider_name)
        
        try:
            # 1. Connect and Validate
            conn_data = await provider.connect(credentials)
            ext_account_id = conn_data.get("external_account_id")
            
            # 2. Get DB Provider ID
            result = await self.db.execute(select(IntegrationProvider).filter_by(name=provider_name))
            db_provider = result.scalar_one_or_none()
            if not db_provider:
                raise ValueError(f"Database configuration for {provider_name} missing")
                
            # 3. Store Encrypted Credentials
            await self.auth.store_credentials(user_id, db_provider.id, credentials)
            
            # 4. Create Account Record
            account = ConnectedAccount(
                user_id=user_id,
                provider_id=db_provider.id,
                external_account_id=ext_account_id,
                status="active"
            )
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)
            
            await self.audit.log(user_id, "connect", "success", provider=provider_name)
            return account
            
        except Exception as e:
            await self.audit.log(user_id, "connect", "failure", provider=provider_name, details={"error": str(e)})
            raise e

    async def disconnect_provider(self, user_id: int, account_id: int) -> bool:
        account = await self.db.get(ConnectedAccount, account_id)
        if not account or account.user_id != user_id:
            raise ValueError("Account not found")
            
        result = await self.db.execute(select(IntegrationProvider).filter_by(id=account.provider_id))
        provider_model = result.scalar_one_or_none()
        provider = self._get_provider(provider_model.name)
        
        try:
            await provider.disconnect(account.external_account_id)
            await self.auth.delete_credentials(user_id, account.provider_id)
            
            account.status = "disconnected"
            await self.db.commit()
            await self.audit.log(user_id, "disconnect", "success", provider=provider_model.name)
            return True
        except Exception as e:
            await self.audit.log(user_id, "disconnect", "failure", provider=provider_model.name, details={"error": str(e)})
            raise e

    # --- Sync ---
    async def trigger_sync(self, user_id: int, account_id: int) -> SyncJob:
        account = await self.db.get(ConnectedAccount, account_id)
        if not account or account.user_id != user_id:
            raise ValueError("Account not found")
            
        result = await self.db.execute(select(IntegrationProvider).filter_by(id=account.provider_id))
        provider_model = result.scalar_one_or_none()
        provider = self._get_provider(provider_model.name)

        job = SyncJob(user_id=user_id, account_id=account.id)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # In production, dispatch `self.sync_engine.execute_sync` to a background Redis worker.
        # We invoke directly here for simplicity since wait_ms_before_async isn't blocking.
        import asyncio
        asyncio.create_task(self.sync_engine.execute_sync(job.id, provider, account))
        
        await self.audit.log(user_id, "sync_triggered", "success", provider=provider_model.name)
        return job

    # --- Import / Export ---
    async def start_import(self, user_id: int, file_name: str, file_type: str, import_type: str, content: str) -> ImportJob:
        job = ImportJob(user_id=user_id, file_name=file_name, file_type=file_type, import_type=import_type)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # Dispatch background import
        import asyncio
        asyncio.create_task(self.importer.process_import(job.id, content))
        
        await self.audit.log(user_id, "import_triggered", "success", details={"file_name": file_name})
        return job

    async def start_export(self, user_id: int, export_type: str, fmt: str, filters: Optional[Dict[str, Any]] = None) -> ExportJob:
        job = ExportJob(user_id=user_id, export_type=export_type, format=fmt)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)

        # Dispatch background export
        import asyncio
        asyncio.create_task(self.exporter.process_export(job.id, filters or {}))
        
        await self.audit.log(user_id, "export_triggered", "success", details={"export_type": export_type})
        return job

    async def get_health(self) -> Dict[str, str]:
        healths = {}
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.health()
                healths[name] = "ok" if is_healthy else "degraded"
            except:
                healths[name] = "offline"
        return healths
