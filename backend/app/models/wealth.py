from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

class AccountType(str, enum.Enum):
    CASH = "Cash"
    SAVINGS = "Savings"
    CURRENT = "Current Account"
    CREDIT_CARD = "Credit Card"
    LOAN = "Loan"
    INVESTMENT = "Investment Account"

class AccountStatus(str, enum.Enum):
    ACTIVE = "Active"
    CLOSED = "Closed"

class TransactionType(str, enum.Enum):
    INCOME = "Income"
    EXPENSE = "Expense"
    TRANSFER = "Transfer"
    INVESTMENT = "Investment"
    LOAN_PAYMENT = "Loan Payment"
    INTEREST = "Interest"
    DIVIDEND = "Dividend"
    TAX = "Tax"
    REFUND = "Refund"
    FEE = "Fee"

class BudgetType(str, enum.Enum):
    MONTHLY = "Monthly Budget"
    CATEGORY = "Category Budget"
    CUSTOM = "Custom Budget"

class GoalType(str, enum.Enum):
    EMERGENCY = "Emergency Fund"
    VACATION = "Vacation"
    CAR = "Car"
    HOUSE = "House"
    EDUCATION = "Education"
    RETIREMENT = "Retirement"
    CUSTOM = "Custom Goals"

class Account(Base):
    __tablename__ = "wealth_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    institution = Column(String, nullable=True)
    account_type = Column(Enum(AccountType), nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    transactions = relationship("WealthTransaction", back_populates="account", cascade="all, delete-orphan")

class WealthTransaction(Base):
    __tablename__ = "wealth_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("wealth_accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    currency = Column(String, default="USD")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    notes = Column(String, nullable=True)
    tags = Column(String, nullable=True) # comma separated
    is_recurring = Column(Boolean, default=False)
    attachments_ready = Column(Boolean, default=False)
    
    account = relationship("Account", back_populates="transactions")

class Budget(Base):
    __tablename__ = "wealth_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    budget_type = Column(Enum(BudgetType), nullable=False)
    category = Column(String, nullable=True) # Null for global Monthly Budget
    spending_limit = Column(Float, nullable=False)
    period = Column(String, default="monthly") # e.g. monthly, weekly, yearly
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class FinancialGoal(Base):
    __tablename__ = "wealth_financial_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_progress = Column(Float, default=0.0)
    monthly_contribution = Column(Float, default=0.0)
    estimated_completion_date = Column(DateTime, nullable=True)
    probability = Column(Float, default=0.0) # 0 to 100
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
