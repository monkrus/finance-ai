import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from app.notifications.queue import NotificationQueue
from app.notifications.delivery import NotificationService
from app.models.notification import Notification, NotificationPreference
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class NotificationWorker:
    """
    Background worker that dequeues notifications from Redis and dispatches them 
    via the NotificationService based on user preferences.
    """
    def __init__(self):
        self.queue = NotificationQueue()

    def _should_deliver(self, pref: NotificationPreference, category: str, provider: str) -> bool:
        """Evaluates user preferences and DND hours to decide if a provider should be used."""
        # 1. Global Toggles
        if provider == "email" and not pref.email_enabled: return False
        if provider == "push" and not pref.push_enabled: return False
        if provider == "in_app" and not pref.in_app_enabled: return False
        
        # 2. Category Overrides
        cat_prefs = pref.category_preferences.get(category, {})
        if provider in cat_prefs and not cat_prefs[provider]:
            return False
            
        # 3. Do Not Disturb (Simple UTC check)
        if pref.dnd_start_time and pref.dnd_end_time:
            now_hour = datetime.now(timezone.utc).strftime("%H:%M")
            if pref.dnd_start_time <= now_hour or now_hour <= pref.dnd_end_time:
                # If in DND, suppress push and email, but allow in-app
                if provider in ["push", "email"]:
                    return False
                    
        return True

    async def process_batch(self):
        messages = await self.queue.dequeue(batch_size=50)
        if not messages:
            return

        async with AsyncSessionLocal() as db:
            service = NotificationService(db)
            
            for msg in messages:
                notification_id = msg.get("notification_id")
                if not notification_id:
                    continue
                    
                # Fetch Notification and Preferences
                result = await db.execute(select(Notification).where(Notification.id == notification_id))
                notification = result.scalar_one_or_none()
                if not notification:
                    continue
                    
                pref_result = await db.execute(select(NotificationPreference).where(NotificationPreference.user_id == notification.user_id))
                pref = pref_result.scalar_one_or_none() or NotificationPreference(user_id=notification.user_id)
                
                # Determine Active Providers
                active_providers = []
                for p in ["email", "push", "in_app"]:
                    if self._should_deliver(pref, notification.category, p):
                        active_providers.append(p)
                
                if active_providers:
                    # Deliver
                    await service.deliver(notification, active_providers)
                    
                # Mark as delivered internally (UI delivery tracking)
                notification.delivered_at = datetime.now(timezone.utc)
                db.add(notification)
                
            await db.commit()

async def run_worker_loop():
    """Infinite loop for the background worker task."""
    logger.info("Starting Notification Worker...")
    worker = NotificationWorker()
    while True:
        try:
            await worker.process_batch()
            await asyncio.sleep(0.5) # Poll every 500ms
        except Exception as e:
            logger.error(f"Worker exception: {e}")
            await asyncio.sleep(5.0) # Backoff on crash
