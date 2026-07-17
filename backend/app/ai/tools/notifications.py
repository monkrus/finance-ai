import json
from app.ai.models import AITool
from app.ai.tool_registry import ToolRegistry
from app.core.database import AsyncSessionLocal
from app.notifications.engine import NotificationEngine
from app.schemas.notification import NotificationCreate

async def _create_notification(user_id: int, title: str, message: str, category: str, priority: str = "normal"):
    async with AsyncSessionLocal() as db:
        engine = NotificationEngine(db)
        notification = await engine.create_notification(NotificationCreate(
            user_id=user_id,
            title=title,
            message=message,
            category=category,
            priority=priority
        ))
        return f"Notification created successfully with ID: {notification.id}"

async def _list_notifications(user_id: int, unread_only: bool = False, category: str = None):
    async with AsyncSessionLocal() as db:
        engine = NotificationEngine(db)
        notifs = await engine.get_user_notifications(user_id, unread_only, category, limit=10)
        return json.dumps([
            {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read} 
            for n in notifs
        ])

async def _archive_notification(user_id: int, notification_id: int):
    async with AsyncSessionLocal() as db:
        engine = NotificationEngine(db)
        success = await engine.archive(user_id, notification_id)
        return "Archived successfully." if success else "Notification not found."

async def _dismiss_notification(user_id: int, notification_id: int):
    async with AsyncSessionLocal() as db:
        engine = NotificationEngine(db)
        success = await engine.mark_as_read(user_id, notification_id)
        return "Dismissed successfully." if success else "Notification not found."

# Fake wrappers for alert generators, normally these would be triggered by cron, but AI can trigger a sync check.
async def _portfolio_alerts(user_id: int):
    from app.notifications.generators import AlertGenerator
    async with async_session() as db:
        gen = AlertGenerator(db)
        await gen.run_portfolio_checks(user_id)
        return "Portfolio checks completed and alerts generated if thresholds met."

def register_notification_tools(registry: ToolRegistry):
    registry.register(
        AITool(
            name="create_notification",
            description="Create a new notification for the user. Use this when the AI detects important insights that should proactively alert the user.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "message": {"type": "string"},
                    "category": {"type": "string", "enum": ["system", "portfolio", "market", "news", "wealth", "ai"]},
                    "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]}
                },
                "required": ["user_id", "title", "message", "category"]
            }
        ),
        _create_notification
    )
    
    registry.register(
        AITool(
            name="list_notifications",
            description="List recent notifications for the user.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "unread_only": {"type": "boolean"},
                    "category": {"type": "string"}
                },
                "required": ["user_id"]
            }
        ),
        _list_notifications
    )
    
    registry.register(
        AITool(
            name="archive_notification",
            description="Archive a specific notification by its ID.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "notification_id": {"type": "integer"}
                },
                "required": ["user_id", "notification_id"]
            }
        ),
        _archive_notification
    )

    registry.register(
        AITool(
            name="dismiss_notification",
            description="Mark a specific notification as read (dismissed).",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "notification_id": {"type": "integer"}
                },
                "required": ["user_id", "notification_id"]
            }
        ),
        _dismiss_notification
    )
    
    registry.register(
        AITool(
            name="portfolio_alerts",
            description="Trigger a manual check for portfolio alerts and generate notifications if thresholds are met.",
            parameters={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"]
            }
        ),
        _portfolio_alerts
    )
