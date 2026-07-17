from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.database import AsyncSessionLocal
from app.integrations.engine import IntegrationEngine
from app.ai.gateway import tool_registry

# AI must never communicate with providers directly. Everything routes through IntegrationEngine.

class ProviderConnectSchema(BaseModel):
    user_id: int = Field(description="The internal user ID")
    provider_name: str = Field(description="The provider name (e.g. mock_bank, mock_broker)")
    credentials: Dict[str, str] = Field(description="The credentials payload")

@tool_registry.register("connect_provider", "Connect an external financial provider.")
async def _connect_provider(payload: ProviderConnectSchema) -> Dict[str, Any]:
    async with AsyncSessionLocal() as db:
        engine = IntegrationEngine(db)
        account = await engine.connect_provider(payload.user_id, payload.provider_name, payload.credentials)
        return {"status": "success", "account_id": account.id}

class SyncAccountSchema(BaseModel):
    user_id: int = Field(description="The internal user ID")
    account_id: int = Field(description="The connected account ID")

@tool_registry.register("sync_accounts", "Trigger a sync for a connected account.")
async def _sync_accounts(payload: SyncAccountSchema) -> Dict[str, Any]:
    async with AsyncSessionLocal() as db:
        engine = IntegrationEngine(db)
        job = await engine.trigger_sync(payload.user_id, payload.account_id)
        return {"status": "success", "job_id": job.id}

class ImportSchema(BaseModel):
    user_id: int = Field(description="The internal user ID")
    file_name: str = Field(description="The name of the file")
    file_type: str = Field(description="csv, excel, or json")
    import_type: str = Field(description="transactions or portfolio")
    content: str = Field(description="The raw string content")

@tool_registry.register("import_transactions", "Import transactions via file.")
async def _import_transactions(payload: ImportSchema) -> Dict[str, Any]:
    async with AsyncSessionLocal() as db:
        engine = IntegrationEngine(db)
        job = await engine.start_import(payload.user_id, payload.file_name, payload.file_type, payload.import_type, payload.content)
        return {"status": "queued", "job_id": job.id}

class ProviderHealthSchema(BaseModel):
    pass

@tool_registry.register("provider_health", "Check the health of all external providers.")
async def _provider_health(payload: ProviderHealthSchema) -> Dict[str, str]:
    async with AsyncSessionLocal() as db:
        engine = IntegrationEngine(db)
        return await engine.get_health()

@tool_registry.register("integration_summary", "Get a summary of external integration capabilities.")
async def _integration_summary(payload: ProviderHealthSchema) -> Dict[str, Any]:
    async with AsyncSessionLocal() as db:
        engine = IntegrationEngine(db)
        providers = await engine.get_providers()
        return {"available_providers": [p.name for p in providers]}
