from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.wealth import Budget, WealthTransaction, BudgetType
from datetime import datetime, timezone
import calendar

class BudgetEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_budget_utilization(self, user_id: int, year: int, month: int) -> dict:
        # Get start and end of month
        start_date = datetime(year, month, 1, tzinfo=timezone.utc)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

        # Get all budgets for user
        result = await self.db.execute(select(Budget).where(Budget.user_id == user_id))
        budgets = result.scalars().all()

        # Get all expenses for user in month
        tx_result = await self.db.execute(
            select(WealthTransaction).where(
                WealthTransaction.user_id == user_id,
                WealthTransaction.transaction_type == "Expense",
                WealthTransaction.timestamp >= start_date,
                WealthTransaction.timestamp <= end_date
            )
        )
        expenses = tx_result.scalars().all()

        # Calculate global monthly budget
        monthly_budgets = [b for b in budgets if b.budget_type == BudgetType.MONTHLY]
        global_limit = sum(b.spending_limit for b in monthly_budgets)
        
        # Calculate spending per category
        category_spending = {}
        total_spending = 0.0
        
        for exp in expenses:
            total_spending += exp.amount
            if exp.category:
                category_spending[exp.category] = category_spending.get(exp.category, 0.0) + exp.amount

        utilizations = []
        
        # Add monthly budget utilization
        if global_limit > 0:
            utilizations.append({
                "budget_type": "Monthly Budget",
                "category": None,
                "limit": global_limit,
                "spent": total_spending,
                "remaining": global_limit - total_spending,
                "utilization_percentage": (total_spending / global_limit) * 100,
                "overspent": total_spending > global_limit
            })

        # Add category budgets
        for b in budgets:
            if b.budget_type == BudgetType.CATEGORY and b.category:
                spent = category_spending.get(b.category, 0.0)
                utilizations.append({
                    "budget_type": "Category Budget",
                    "category": b.category,
                    "limit": b.spending_limit,
                    "spent": spent,
                    "remaining": b.spending_limit - spent,
                    "utilization_percentage": (spent / b.spending_limit) * 100 if b.spending_limit > 0 else 0,
                    "overspent": spent > b.spending_limit
                })

        # Burn rate is total spending / days passed in month
        current_day = datetime.now(timezone.utc).day if (year == datetime.now(timezone.utc).year and month == datetime.now(timezone.utc).month) else last_day
        monthly_burn_rate = total_spending / current_day if current_day > 0 else 0.0

        return {
            "budgets": utilizations,
            "total_spent": total_spending,
            "monthly_burn_rate_per_day": monthly_burn_rate,
            "projected_monthly_spend": monthly_burn_rate * last_day
        }
