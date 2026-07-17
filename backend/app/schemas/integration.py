from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

# --- Integration Provider ---
class IntegrationProviderBase(BaseModel):
    name: str
    provider_type: str
    is_active: bool = True

class IntegrationProviderResponse(IntegrationProviderBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Connected Account ---
class ConnectedAccountBase(BaseModel):
    provider_id: int
    external_account_id: str
    sync_frequency: str = "daily"

class ConnectedAccountCreate(ConnectedAccountBase):
    credentials: Dict[str, str]

class ConnectedAccountResponse(ConnectedAccountBase):
    id: int
    user_id: int
    status: str
    sync_status: str
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Sync Job ---
class SyncJobResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    status: str
    sync_type: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Import Job ---
class ImportJobResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    import_type: str
    status: str
    records_processed: int
    records_failed: int
    error_log: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Export Job ---
class ExportJobCreate(BaseModel):
    export_type: str
    format: str
    filters: Optional[Dict[str, Any]] = None

class ExportJobResponse(BaseModel):
    id: int
    user_id: int
    export_type: str
    format: str
    status: str
    file_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Audit Event ---
class AuditEventResponse(BaseModel):
    id: int
    user_id: int
    action: str
    provider: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
