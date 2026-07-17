from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

from app.integrations.engine import IntegrationEngine
from app.schemas.integration import (
    IntegrationProviderResponse,
    ConnectedAccountCreate,
    ConnectedAccountResponse,
    SyncJobResponse,
    ImportJobResponse,
    ExportJobCreate,
    ExportJobResponse,
    AuditEventResponse
)
from app.models.integration import ConnectedAccount, SyncJob, ImportJob, ExportJob, AuditEvent

router = APIRouter()

def get_engine(db: AsyncSession = Depends(get_db)) -> IntegrationEngine:
    return IntegrationEngine(db)

@router.get("/providers", response_model=List[IntegrationProviderResponse])
async def list_providers(engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    return await engine.get_providers()

@router.post("/connect", response_model=ConnectedAccountResponse)
async def connect_provider(payload: ConnectedAccountCreate, engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    # Look up provider name by ID (in a real app, API would pass the name or id directly)
    result = await engine.db.execute(select(engine.db.class_mapper(engine.db.get(ConnectedAccount, 1)).class_).filter_by(id=payload.provider_id)) # Not ideal mapping here for simplicity
    
    from app.models.integration import IntegrationProvider
    provider = await engine.db.get(IntegrationProvider, payload.provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    try:
        return await engine.connect_provider(user.id, provider.name, payload.credentials)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/disconnect/{account_id}")
async def disconnect_provider(account_id: int, engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    try:
        await engine.disconnect_provider(user.id, account_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sync/{account_id}", response_model=SyncJobResponse)
async def trigger_sync(account_id: int, engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    try:
        return await engine.trigger_sync(user.id, account_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import", response_model=ImportJobResponse)
async def start_import(file_name: str, file_type: str, import_type: str, content: str, engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    return await engine.start_import(user.id, file_name, file_type, import_type, content)

@router.post("/export", response_model=ExportJobResponse)
async def start_export(payload: ExportJobCreate, engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    return await engine.start_export(user.id, payload.export_type, payload.format, payload.filters)

@router.get("/jobs/sync", response_model=List[SyncJobResponse])
async def list_sync_jobs(engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    res = await engine.db.execute(select(SyncJob).filter_by(user_id=user.id))
    return list(res.scalars().all())

@router.get("/audit", response_model=List[AuditEventResponse])
async def list_audit_events(engine: IntegrationEngine = Depends(get_engine), user: User = Depends(get_current_user)):
    res = await engine.db.execute(select(AuditEvent).filter_by(user_id=user.id))
    return list(res.scalars().all())

@router.get("/health")
async def provider_health(engine: IntegrationEngine = Depends(get_engine)):
    return await engine.get_health()
