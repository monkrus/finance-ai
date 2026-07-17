from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class WidgetSchema(BaseModel):
    title: str
    subtitle: Optional[str] = None
    value: Any
    formatted_value: Optional[str] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None # up, down, flat
    status: Optional[str] = None # neutral, warning, danger, success
    priority: Optional[int] = 0
    icon: Optional[str] = None
    color: Optional[str] = None
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = {}

class DashboardSectionBase(BaseModel):
    widgets: List[WidgetSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

class OverviewSection(DashboardSectionBase):
    pass

class PortfolioSection(DashboardSectionBase):
    pass

class MarketSection(DashboardSectionBase):
    pass

class NewsSection(DashboardSectionBase):
    pass

class WealthSection(DashboardSectionBase):
    pass

class WatchlistSection(DashboardSectionBase):
    pass

class CalendarSection(DashboardSectionBase):
    pass

class InsightsSection(DashboardSectionBase):
    pass

class DashboardResponse(BaseModel):
    overview: Optional[OverviewSection] = None
    portfolio: Optional[PortfolioSection] = None
    market: Optional[MarketSection] = None
    news: Optional[NewsSection] = None
    wealth: Optional[WealthSection] = None
    watchlist: Optional[WatchlistSection] = None
    calendar: Optional[CalendarSection] = None
    insights: Optional[InsightsSection] = None
