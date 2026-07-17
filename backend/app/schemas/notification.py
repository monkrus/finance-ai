from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    category: str
    priority: str = "normal"
    expires_at: Optional[datetime] = None
    metadata_payload: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    is_archived: bool
    is_pinned: bool
    snoozed_until: Optional[datetime] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RuleConditionNode(BaseModel):
    # A simplified nested condition structure
    target: Optional[str] = None # e.g. "AAPL.price", "portfolio.total_loss"
    operator: Optional[str] = None # e.g. ">", "<", "=="
    value: Optional[Any] = None
    AND: Optional[List['RuleConditionNode']] = None
    OR: Optional[List['RuleConditionNode']] = None

class NotificationRuleBase(BaseModel):
    name: str
    is_active: bool = True
    priority: str = "normal"
    condition_json: Dict[str, Any] # Will map to RuleConditionNode in processing
    action_type: str = "notify"
    message_template: Optional[str] = None
    cooldown_minutes: int = 60

class NotificationRuleCreate(NotificationRuleBase):
    pass

class NotificationRuleResponse(NotificationRuleBase):
    id: int
    user_id: int
    last_triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationPreferenceBase(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    category_preferences: Dict[str, Dict[str, bool]] = {}
    dnd_start_time: Optional[str] = None
    dnd_end_time: Optional[str] = None

class NotificationPreferenceUpdate(NotificationPreferenceBase):
    pass

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    category: str
    subject_template: str
    body_template: str
    is_active: bool

    class Config:
        from_attributes = True
