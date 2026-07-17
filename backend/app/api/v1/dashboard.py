from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.dashboard.schemas import (
    OverviewSection, PortfolioSection, MarketSection, NewsSection,
    WealthSection, WatchlistSection, CalendarSection, InsightsSection,
    DashboardResponse
)
from app.dashboard.engine import DashboardEngine

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardResponse)
async def get_full_dashboard(
    sections: Optional[str] = Query(None, description="Comma separated list of sections to fetch"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    section_list = sections.split(",") if sections else None
    engine = DashboardEngine(db)
    return await engine.get_dashboard(current_user.id, section_list)

@router.get("/overview", response_model=OverviewSection)
async def get_overview(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["overview"])
    return res.overview

@router.get("/portfolio", response_model=PortfolioSection)
async def get_portfolio(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["portfolio"])
    return res.portfolio

@router.get("/market", response_model=MarketSection)
async def get_market(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["market"])
    return res.market

@router.get("/news", response_model=NewsSection)
async def get_news(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["news"])
    return res.news

@router.get("/wealth", response_model=WealthSection)
async def get_wealth(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["wealth"])
    return res.wealth

@router.get("/watchlist", response_model=WatchlistSection)
async def get_watchlist(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["watchlist"])
    return res.watchlist

@router.get("/calendar", response_model=CalendarSection)
async def get_calendar(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["calendar"])
    return res.calendar

@router.get("/insights", response_model=InsightsSection)
async def get_insights(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = DashboardEngine(db)
    res = await engine.get_dashboard(current_user.id, ["insights"])
    return res.insights
