from app.dashboard.schemas import WidgetSchema
from datetime import datetime, timezone
from typing import Any, Optional, Dict

class WidgetBuilder:
    @staticmethod
    def build(
        title: str,
        value: Any,
        subtitle: Optional[str] = None,
        formatted_value: Optional[str] = None,
        change: Optional[float] = None,
        change_percent: Optional[float] = None,
        trend: Optional[str] = None,
        status: Optional[str] = None,
        priority: int = 0,
        icon: Optional[str] = None,
        color: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WidgetSchema:
        
        # Auto-detect trend if not provided
        if trend is None and change is not None:
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            else:
                trend = "flat"
                
        # Auto-detect status if not provided (assume standard financial status)
        if status is None and change is not None:
            if change > 0:
                status = "success"
            elif change < 0:
                status = "danger"
            else:
                status = "neutral"

        return WidgetSchema(
            title=title,
            subtitle=subtitle,
            value=value,
            formatted_value=formatted_value,
            change=change,
            change_percent=change_percent,
            trend=trend,
            status=status,
            priority=priority,
            icon=icon,
            color=color,
            last_updated=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
