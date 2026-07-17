from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.wealth import WealthTransaction, TransactionType
from datetime import datetime, timezone
import calendar

class CashFlowEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_monthly_cashflow(self, user_id: int, year: int, month: int) -> dict:
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

        result = await self.db.execute(
            select(WealthTransaction).where(
                WealthTransaction.user_id == user_id,
                WealthTransaction.timestamp >= start_date,
                WealthTransaction.timestamp <= end_date
            )
        )
        transactions = result.scalars().all()

        total_income = 0.0
        total_expenses = 0.0
        income_breakdown = {}
        expense_breakdown = {}

        for tx in transactions:
            if tx.transaction_type in [TransactionType.INCOME, TransactionType.INTEREST, TransactionType.DIVIDEND, TransactionType.REFUND]:
                total_income += tx.amount
                cat = tx.category or "Other Income"
                income_breakdown[cat] = income_breakdown.get(cat, 0.0) + tx.amount
            elif tx.transaction_type in [TransactionType.EXPENSE, TransactionType.FEE, TransactionType.TAX]:
                total_expenses += tx.amount
                cat = tx.category or "Other Expenses"
                expense_breakdown[cat] = expense_breakdown.get(cat, 0.0) + tx.amount

        free_cash_flow = total_income - total_expenses
        savings_rate = (free_cash_flow / total_income) * 100 if total_income > 0 else 0.0

        return {
            "month": f"{year}-{month:02d}",
            "total_income": total_income,
            "total_expenses": total_expenses,
            "free_cash_flow": free_cash_flow,
            "savings_rate_percentage": savings_rate,
            "income_breakdown": income_breakdown,
            "expense_breakdown": expense_breakdown
        }
