from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio as PortfolioModel, Transaction as TransactionModel, Holding as HoldingModel
from app.schemas.portfolio import (
    Portfolio, PortfolioCreate, Transaction, TransactionCreate, 
    PortfolioAnalytics, Holding
)
from app.portfolio.engine import PortfolioEngine
from app.portfolio.transaction import TransactionEngine
from app.market_data.service import MarketDataService
from app.analysis.engine import AnalysisEngine

router = APIRouter()

def get_portfolio_engine() -> PortfolioEngine:
    md = MarketDataService()
    analysis = AnalysisEngine(md)
    return PortfolioEngine(market_data_service=md, analysis_engine=analysis)

def get_transaction_engine() -> TransactionEngine:
    return TransactionEngine()

@router.post("/", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_portfolio = PortfolioModel(
        user_id=current_user.id,
        name=portfolio.name,
        description=portfolio.description,
        currency=portfolio.currency,
        is_public=portfolio.is_public
    )
    db.add(db_portfolio)
    await db.commit()
    
    result = await db.execute(
        select(PortfolioModel)
        .options(selectinload(PortfolioModel.holdings), selectinload(PortfolioModel.transactions))
        .filter(PortfolioModel.id == db_portfolio.id)
    )
    return result.scalars().first()

from sqlalchemy.orm import selectinload

@router.get("/", response_model=List[Portfolio])
async def get_portfolios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PortfolioModel)
        .options(selectinload(PortfolioModel.holdings), selectinload(PortfolioModel.transactions))
        .filter(PortfolioModel.user_id == current_user.id)
    )
    return result.scalars().all()

@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PortfolioModel)
        .options(selectinload(PortfolioModel.holdings), selectinload(PortfolioModel.transactions))
        .filter(
            PortfolioModel.id == portfolio_id,
            PortfolioModel.user_id == current_user.id
        )
    )
    portfolio = result.scalars().first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.post("/{portfolio_id}/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    portfolio_id: int,
    transaction: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tx_engine: TransactionEngine = Depends(get_transaction_engine)
):
    result = await db.execute(select(PortfolioModel).filter(
        PortfolioModel.id == portfolio_id,
        PortfolioModel.user_id == current_user.id
    ))
    portfolio = result.scalars().first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    try:
        tx = await tx_engine.process_transaction(db, portfolio_id, transaction)
        return tx
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{portfolio_id}/holdings", response_model=List[Holding])
async def get_portfolio_holdings(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PortfolioEngine = Depends(get_portfolio_engine)
):
    """Holdings enriched with market data (price, market value, weight, sector)."""
    result = await db.execute(select(PortfolioModel).filter(
        PortfolioModel.id == portfolio_id,
        PortfolioModel.user_id == current_user.id
    ))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return await engine.get_hydrated_holdings(db, portfolio_id)

@router.get("/{portfolio_id}/analytics", response_model=PortfolioAnalytics)
async def get_portfolio_analytics(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    engine: PortfolioEngine = Depends(get_portfolio_engine)
):
    result = await db.execute(select(PortfolioModel).filter(
        PortfolioModel.id == portfolio_id,
        PortfolioModel.user_id == current_user.id
    ))
    portfolio = result.scalars().first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    try:
        analytics = await engine.get_portfolio_analytics(db, portfolio_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
