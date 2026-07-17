import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime, timezone
import json

from app.models.notification import Notification, NotificationRule, NotificationPreference
from app.schemas.notification import NotificationCreate
from app.notifications.rules import RulesEngine
from app.notifications.queue import NotificationQueue

logger = logging.getLogger(__name__)

class NotificationEngine:
    """Central engine for managing and dispatching notifications."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rules_engine = RulesEngine()
        self.queue = NotificationQueue()

    async def create_notification(self, data: NotificationCreate) -> Notification:
        """
        Directly creates a notification in the DB and enqueues it for Delivery.
        Used by the AI agents or background generators.
        """
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            category=data.category,
            priority=data.priority,
            expires_at=data.expires_at,
            metadata_payload=data.metadata_payload
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        
        # Enqueue for background delivery
        await self.queue.enqueue({
            "notification_id": notification.id,
            "user_id": notification.user_id,
            "title": notification.title,
            "category": notification.category
        })
        
        return notification

    async def process_event(self, user_id: int, event_category: str, payload: Dict[str, Any]):
        """
        Evaluates a raw event payload against the user's custom Notification Rules.
        If a rule matches, a Notification is created.
        """
        # Fetch active rules for the user
        result = await self.db.execute(
            select(NotificationRule)
            .where(NotificationRule.user_id == user_id)
            .where(NotificationRule.is_active == True)
        )
        rules = result.scalars().all()
        
        for rule in rules:
            # Basic cooldown check
            if rule.last_triggered_at:
                delta = datetime.now(timezone.utc) - rule.last_triggered_at
                if delta.total_seconds() < (rule.cooldown_minutes * 60):
                    continue
            
            # Evaluate rule
            if self.rules_engine.evaluate(rule.condition_json, payload):
                # Rule matches! Generate notification.
                # In a real app, message_template would be rendered with Jinja2 using `payload`.
                message = rule.message_template or f"Rule '{rule.name}' triggered!"
                
                await self.create_notification(NotificationCreate(
                    user_id=user_id,
                    title=f"Alert: {rule.name}",
                    message=message,
                    category=event_category,
                    priority=rule.priority,
                    metadata_payload=payload
                ))
                
                # Update cooldown
                rule.last_triggered_at = datetime.now(timezone.utc)
                self.db.add(rule)
                await self.db.commit()

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False, category: Optional[str] = None, limit: int = 50
    ) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id).where(Notification.is_archived == False)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        if category:
            query = query.where(Notification.category == category)
            
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
        
    async def get_user_preferences(self, user_id: int) -> NotificationPreference:
        result = await self.db.execute(select(NotificationPreference).where(NotificationPreference.user_id == user_id))
        pref = result.scalar_one_or_none()
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.db.add(pref)
            await self.db.commit()
            await self.db.refresh(pref)
        return pref

    async def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def archive(self, user_id: int, notification_id: int) -> bool:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_archived=True)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def snooze(self, user_id: int, notification_id: int, until: datetime) -> bool:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(snoozed_until=until, is_read=False)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
