from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from app.models.wealth import AccountType, AccountStatus, TransactionType, BudgetType, GoalType

class AccountBase(BaseModel):
    name: str
    balance: float = 0.0
    currency: str = "USD"
    institution: Optional[str] = None
    account_type: AccountType
    status: AccountStatus = AccountStatus.ACTIVE

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    account_id: int
    amount: float
    transaction_type: TransactionType
    category: Optional[str] = None
    merchant: Optional[str] = None
    currency: str = "USD"
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None
    tags: Optional[str] = None
    is_recurring: bool = False
    attachments_ready: bool = False

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class BudgetBase(BaseModel):
    budget_type: BudgetType
    category: Optional[str] = None
    spending_limit: float
    period: str = "monthly"

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FinancialGoalBase(BaseModel):
    goal_type: GoalType
    name: str
    target_amount: float
    current_progress: float = 0.0
    monthly_contribution: float = 0.0

class FinancialGoalCreate(FinancialGoalBase):
    pass

class FinancialGoalResponse(FinancialGoalBase):
    id: int
    user_id: int
    estimated_completion_date: Optional[datetime] = None
    probability: float = 0.0
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
