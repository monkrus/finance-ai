from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import Optional

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True) # e.g. "portfolio", "market", "news"
    priority = Column(String, nullable=False, default="normal") # low, normal, high, critical
    
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    snoozed_until = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata_payload = Column(JSON, nullable=True) # Extra data for frontend routing, AI context

    user = relationship("User")

class NotificationRule(Base):
    __tablename__ = "notification_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(String, default="normal")
    
    # JSON logic tree. e.g. {"AND": [{"target": "price", "operator": ">", "value": 500}]}
    condition_json = Column(JSON, nullable=False)
    
    action_type = Column(String, default="notify") # Can be used later for automations
    message_template = Column(String, nullable=True)
    
    cooldown_minutes = Column(Integer, default=60) # Prevent spam
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Global toggles
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Category level settings stored as JSON
    # e.g. {"market": {"email": True, "push": False}, "news": {"email": False}}
    category_preferences = Column(JSON, default={})
    
    # Do Not Disturb
    dnd_start_time = Column(String, nullable=True) # e.g. "22:00"
    dnd_end_time = Column(String, nullable=True) # e.g. "07:00"
    
    user = relationship("User")

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False) # e.g., "email", "push", "webhook"
    
    status = Column(String, nullable=False, default="pending") # pending, delivered, failed
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    notification = relationship("Notification", backref="deliveries")

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    
    subject_template = Column(String, nullable=False)
    body_template = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
