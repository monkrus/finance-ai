from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.wealth import Account, WealthTransaction, Budget, FinancialGoal
from app.schemas.wealth import (
    AccountCreate, AccountResponse,
    TransactionCreate, TransactionResponse,
    BudgetCreate, BudgetResponse,
    FinancialGoalCreate, FinancialGoalResponse
)
from app.wealth.budget import BudgetEngine
from app.wealth.cashflow import CashFlowEngine
from app.wealth.networth import NetWorthEngine
from app.wealth.goals import GoalEngine
from app.wealth.planning import WealthPlanningEngine
from app.wealth.coach import AIFinancialCoach

router = APIRouter(tags=["Personal Finance"])

# ================= Accounts =================

@router.post("/accounts", response_model=AccountResponse)
async def create_account(account: AccountCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_acc = Account(**account.model_dump(), user_id=current_user.id)
    db.add(db_acc)
    await db.commit()
    await db.refresh(db_acc)
    return db_acc

@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Account).where(Account.user_id == current_user.id))
    return res.scalars().all()

# ================= Transactions =================

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Validate account ownership
    acc_res = await db.execute(select(Account).where(Account.id == tx.account_id, Account.user_id == current_user.id))
    if not acc_res.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized to use this account")
        
    db_tx = WealthTransaction(**tx.model_dump(), user_id=current_user.id)
    db.add(db_tx)
    
    # Update account balance heuristically (Income adds, Expense subtracts)
    acc = (await db.execute(select(Account).where(Account.id == tx.account_id))).scalar_one()
    if tx.transaction_type.value in ["Income", "Interest", "Dividend", "Refund"]:
        acc.balance += tx.amount
    elif tx.transaction_type.value in ["Expense", "Tax", "Fee"]:
        acc.balance -= tx.amount
        
    await db.commit()
    await db.refresh(db_tx)
    return db_tx

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(WealthTransaction).where(WealthTransaction.user_id == current_user.id))
    return res.scalars().all()

# ================= Budgets & Goals =================

@router.post("/budgets", response_model=BudgetResponse)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_b = Budget(**budget.model_dump(), user_id=current_user.id)
    db.add(db_b)
    await db.commit()
    await db.refresh(db_b)
    return db_b

@router.post("/goals", response_model=FinancialGoalResponse)
async def create_goal(goal: FinancialGoalCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_g = FinancialGoal(**goal.model_dump(), user_id=current_user.id)
    db.add(db_g)
    await db.commit()
    await db.refresh(db_g)
    return db_g

# ================= Analytics Engines =================

@router.get("/analytics/budget")
async def get_budget_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    engine = BudgetEngine(db)
    return await engine.calculate_budget_utilization(current_user.id, now.year, now.month)

@router.get("/analytics/cashflow")
async def get_cashflow_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    engine = CashFlowEngine(db)
    return await engine.calculate_monthly_cashflow(current_user.id, now.year, now.month)

@router.get("/analytics/networth")
async def get_networth_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = NetWorthEngine(db)
    return await engine.calculate_net_worth(current_user.id)

@router.get("/analytics/goals")
async def get_goals_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = GoalEngine(db)
    return await engine.calculate_goals_progress(current_user.id)

@router.get("/analytics/planning")
async def get_wealth_plan(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    engine = WealthPlanningEngine(db)
    return await engine.calculate_wealth_plan(current_user.id)

# ================= AI Coach =================

@router.get("/coach/advice")
async def get_ai_advice(query: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    coach = AIFinancialCoach(db)
    return {"advice": await coach.get_financial_advice(current_user.id, query)}
