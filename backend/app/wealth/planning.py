from sqlalchemy.ext.asyncio import AsyncSession
from app.wealth.networth import NetWorthEngine
from app.wealth.cashflow import CashFlowEngine
from datetime import datetime, timezone

class WealthPlanningEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.networth_engine = NetWorthEngine(db)
        self.cashflow_engine = CashFlowEngine(db)

    async def calculate_wealth_plan(self, user_id: int) -> dict:
        now = datetime.now(timezone.utc)
        
        # Gather foundational metrics
        nw_data = await self.networth_engine.calculate_net_worth(user_id)
        cf_data = await self.cashflow_engine.calculate_monthly_cashflow(user_id, now.year, now.month)
        
        total_assets = nw_data.get("total_assets", 0)
        total_liabilities = nw_data.get("total_liabilities", 0)
        cash = nw_data["assets"].get("cash", 0)
        investments = nw_data["assets"].get("investments", 0)
        
        monthly_income = cf_data.get("total_income", 0)
        monthly_expenses = cf_data.get("total_expenses", 0)
        
        # Calculate derived ratios
        debt_to_income_ratio = 0.0
        if monthly_income > 0:
            # Assuming a standard heuristic that 3% of total liabilities is paid monthly
            est_monthly_debt_payment = total_liabilities * 0.03
            debt_to_income_ratio = (est_monthly_debt_payment / monthly_income) * 100
            
        savings_ratio = cf_data.get("savings_rate_percentage", 0)
        
        # Emergency Fund Coverage (Months)
        emergency_fund_months = 0.0
        if monthly_expenses > 0:
            emergency_fund_months = cash / monthly_expenses
            
        investment_ratio = (investments / total_assets) * 100 if total_assets > 0 else 0
        
        # FIRE Progress (Foundation)
        # Using 4% rule (25x annual expenses)
        annual_expenses = monthly_expenses * 12
        fire_target = annual_expenses * 25
        fire_progress_pct = (investments / fire_target * 100) if fire_target > 0 else 0
        
        # Financial Health Score (0-100)
        health_score = 50 # Base
        
        # Adjust for emergency fund (Target 6 months = +20)
        if emergency_fund_months >= 6: health_score += 20
        elif emergency_fund_months >= 3: health_score += 10
        elif emergency_fund_months < 1: health_score -= 10
        
        # Adjust for DTI (Target < 30% = +15)
        if debt_to_income_ratio < 30: health_score += 15
        elif debt_to_income_ratio > 50: health_score -= 15
        
        # Adjust for savings rate (Target > 20% = +15)
        if savings_ratio >= 20: health_score += 15
        elif savings_ratio <= 0: health_score -= 10
        
        health_score = max(0, min(100, health_score))

        return {
            "financial_health_score": health_score,
            "emergency_fund_coverage_months": emergency_fund_months,
            "debt_to_income_ratio_percentage": debt_to_income_ratio,
            "savings_ratio_percentage": savings_ratio,
            "investment_ratio_percentage": investment_ratio,
            "retirement_readiness": {
                "fire_target": fire_target,
                "current_investments": investments,
                "fire_progress_percentage": fire_progress_pct
            }
        }
