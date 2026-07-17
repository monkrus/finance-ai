import logging
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import NotificationDelivery, Notification

logger = logging.getLogger(__name__)

class NotificationProviderException(Exception):
    pass

class NotificationProvider:
    provider_name = "base"
    
    async def send(self, notification: Notification, payload: Dict[str, Any]) -> bool:
        raise NotImplementedError()

class EmailProvider(NotificationProvider):
    provider_name = "email"
    
    async def send(self, notification: Notification, payload: Dict[str, Any]) -> bool:
        logger.info(f"[EmailProvider] Sending {notification.title} to User {notification.user_id}")
        raise NotImplementedError("Email delivery is not supported yet")

class PushProvider(NotificationProvider):
    provider_name = "push"
    
    async def send(self, notification: Notification, payload: Dict[str, Any]) -> bool:
        logger.info(f"[PushProvider] Sending {notification.title} to User {notification.user_id}")
        raise NotImplementedError("Push notification delivery is not supported yet")

class InAppProvider(NotificationProvider):
    provider_name = "in_app"
    
    async def send(self, notification: Notification, payload: Dict[str, Any]) -> bool:
        # In-app notifications are naturally handled by saving to DB and the UI fetching them.
        # But we could trigger a websocket event here.
        logger.info(f"[InAppProvider] Emitting websocket event for User {notification.user_id}")
        raise NotImplementedError("In-App websocket emission is not supported yet")

class WebhookProvider(NotificationProvider):
    provider_name = "webhook"
    
    async def send(self, notification: Notification, payload: Dict[str, Any]) -> bool:
        logger.info(f"[WebhookProvider] Firing webhook for User {notification.user_id}")
        raise NotImplementedError("Webhook delivery is not supported yet")

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers: Dict[str, NotificationProvider] = {
            "email": EmailProvider(),
            "push": PushProvider(),
            "in_app": InAppProvider(),
            "webhook": WebhookProvider()
        }

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(NotificationProviderException),
        reraise=True
    )
    async def _send_with_retry(self, provider: NotificationProvider, notification: Notification, payload: Dict[str, Any]) -> bool:
        try:
            return await provider.send(notification, payload)
        except Exception as e:
            logger.error(f"Provider {provider.provider_name} failed: {str(e)}")
            raise NotificationProviderException(str(e))

    async def deliver(self, notification: Notification, active_providers: List[str]):
        """Dispatches the notification to multiple providers."""
        for provider_name in active_providers:
            if provider_name not in self.providers:
                continue
                
            provider = self.providers[provider_name]
            delivery = NotificationDelivery(
                notification_id=notification.id,
                provider=provider_name,
                status="pending"
            )
            self.db.add(delivery)
            await self.db.commit()
            
            try:
                # We do this asynchronously but wait for response to record status
                success = await self._send_with_retry(provider, notification, {})
                delivery.status = "delivered" if success else "failed"
            except NotificationProviderException as e:
                delivery.status = "failed"
                delivery.last_error = str(e)
            except Exception as e:
                delivery.status = "failed"
                delivery.last_error = str(e)
            
            self.db.add(delivery)
            await self.db.commit()
