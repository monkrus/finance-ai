from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.wealth import FinancialGoal
from datetime import datetime, timezone
import math

class GoalEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_goals_progress(self, user_id: int) -> dict:
        result = await self.db.execute(select(FinancialGoal).where(FinancialGoal.user_id == user_id))
        goals = result.scalars().all()

        evaluated_goals = []
        for g in goals:
            progress_pct = (g.current_progress / g.target_amount * 100) if g.target_amount > 0 else 0.0
            progress_pct = min(progress_pct, 100.0)
            
            remaining_amount = g.target_amount - g.current_progress
            
            # Calculate months remaining based on monthly contribution
            months_remaining = 0
            if remaining_amount > 0 and g.monthly_contribution > 0:
                months_remaining = math.ceil(remaining_amount / g.monthly_contribution)
            elif remaining_amount > 0 and g.monthly_contribution <= 0:
                months_remaining = -1 # Stalled
            
            # Update estimated completion date heuristically
            est_date = g.estimated_completion_date
            
            # Goal probability heuristics
            probability = g.probability
            if months_remaining > 0 and est_date:
                # If calculated months fit within target date, probability is high
                target_months = (est_date - datetime.now(timezone.utc)).days / 30
                if months_remaining <= target_months:
                    probability = 95.0
                else:
                    probability = max(10.0, 95.0 * (target_months / months_remaining))
            elif remaining_amount <= 0:
                probability = 100.0
                
            evaluated_goals.append({
                "id": g.id,
                "name": g.name,
                "goal_type": g.goal_type,
                "target_amount": g.target_amount,
                "current_progress": g.current_progress,
                "monthly_contribution": g.monthly_contribution,
                "progress_percentage": progress_pct,
                "remaining_amount": remaining_amount,
                "months_remaining": months_remaining,
                "probability": probability
            })
            
        return {
            "total_goals": len(evaluated_goals),
            "completed_goals": sum(1 for g in evaluated_goals if g['progress_percentage'] >= 100.0),
            "goals": evaluated_goals
        }
