import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.wealth.budget import BudgetEngine
from app.wealth.cashflow import CashFlowEngine
from app.wealth.networth import NetWorthEngine
from app.wealth.goals import GoalEngine
from app.wealth.planning import WealthPlanningEngine
from app.models.wealth import BudgetType, TransactionType, AccountType, GoalType
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_budget_engine():
    mock_db = AsyncMock()
    engine = BudgetEngine(mock_db)
    
    # Mock budgets and transactions
    mock_budget = MagicMock()
    mock_budget.budget_type = BudgetType.MONTHLY
    mock_budget.spending_limit = 5000.0
    
    mock_cat_budget = MagicMock()
    mock_cat_budget.budget_type = BudgetType.CATEGORY
    mock_cat_budget.category = "Food"
    mock_cat_budget.spending_limit = 1000.0
    
    mock_tx = MagicMock()
    mock_tx.amount = 1200.0
    mock_tx.category = "Food"
    
    mock_b_res = MagicMock()
    mock_b_res.scalars.return_value.all.return_value = [mock_budget, mock_cat_budget]
    
    mock_tx_res = MagicMock()
    mock_tx_res.scalars.return_value.all.return_value = [mock_tx]
    
    mock_db.execute.side_effect = [mock_b_res, mock_tx_res]
    
    res = await engine.calculate_budget_utilization(1, 2023, 1)
    
    assert res["total_spent"] == 1200.0
    assert len(res["budgets"]) == 2
    
    # Global limit
    assert res["budgets"][0]["limit"] == 5000.0
    assert res["budgets"][0]["spent"] == 1200.0
    assert not res["budgets"][0]["overspent"]
    
    # Category limit
    assert res["budgets"][1]["limit"] == 1000.0
    assert res["budgets"][1]["spent"] == 1200.0
    assert res["budgets"][1]["overspent"]

@pytest.mark.asyncio
async def test_cashflow_engine():
    mock_db = AsyncMock()
    engine = CashFlowEngine(mock_db)
    
    mock_tx_in = MagicMock()
    mock_tx_in.transaction_type = TransactionType.INCOME
    mock_tx_in.amount = 5000.0
    mock_tx_in.category = "Salary"
    
    mock_tx_out = MagicMock()
    mock_tx_out.transaction_type = TransactionType.EXPENSE
    mock_tx_out.amount = 2000.0
    mock_tx_out.category = "Rent"
    
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [mock_tx_in, mock_tx_out]
    mock_db.execute.return_value = mock_res
    
    res = await engine.calculate_monthly_cashflow(1, 2023, 1)
    
    assert res["total_income"] == 5000.0
    assert res["total_expenses"] == 2000.0
    assert res["free_cash_flow"] == 3000.0
    assert res["savings_rate_percentage"] == 60.0

@pytest.mark.asyncio
async def test_networth_engine():
    mock_db = AsyncMock()
    engine = NetWorthEngine(mock_db)
    
    # Mock Accounts
    mock_cash = MagicMock()
    mock_cash.account_type = AccountType.SAVINGS
    mock_cash.balance = 10000.0
    mock_cash.name = "Bank"
    
    mock_debt = MagicMock()
    mock_debt.account_type = AccountType.CREDIT_CARD
    mock_debt.balance = 2000.0
    mock_debt.name = "Card"
    
    mock_acc_res = MagicMock()
    mock_acc_res.scalars.return_value.all.return_value = [mock_cash, mock_debt]
    
    # Mock Portfolios
    mock_port = MagicMock()
    mock_port.id = 1
    mock_port.name = "Investing"
    
    mock_port_res = MagicMock()
    mock_port_res.scalars.return_value.all.return_value = [mock_port]
    
    # Mock Holdings
    mock_hold = MagicMock()
    mock_hold.cost_basis = 15000.0
    
    mock_hold_res = MagicMock()
    mock_hold_res.scalars.return_value.all.return_value = [mock_hold]
    
    mock_db.execute.side_effect = [mock_acc_res, mock_port_res, mock_hold_res]
    
    res = await engine.calculate_net_worth(1)
    
    assert res["total_assets"] == 25000.0 # 10000 + 15000
    assert res["total_liabilities"] == 2000.0
    assert res["net_worth"] == 23000.0
    
@pytest.mark.asyncio
async def test_goals_engine():
    mock_db = AsyncMock()
    engine = GoalEngine(mock_db)
    
    mock_goal = MagicMock()
    mock_goal.target_amount = 10000.0
    mock_goal.current_progress = 5000.0
    mock_goal.monthly_contribution = 1000.0
    mock_goal.estimated_completion_date = None
    mock_goal.probability = 0.0
    
    mock_goal_stalled = MagicMock()
    mock_goal_stalled.target_amount = 5000.0
    mock_goal_stalled.current_progress = 1000.0
    mock_goal_stalled.monthly_contribution = 0.0
    mock_goal_stalled.estimated_completion_date = None
    mock_goal_stalled.probability = 0.0
    
    mock_goal_completed = MagicMock()
    mock_goal_completed.target_amount = 5000.0
    mock_goal_completed.current_progress = 5000.0
    mock_goal_completed.monthly_contribution = 0.0
    mock_goal_completed.estimated_completion_date = None
    mock_goal_completed.probability = 0.0
    
    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [mock_goal, mock_goal_stalled, mock_goal_completed]
    mock_db.execute.return_value = mock_res
    
    res = await engine.calculate_goals_progress(1)
    
    assert res["total_goals"] == 3
    assert res["completed_goals"] == 1
    assert res["goals"][0]["progress_percentage"] == 50.0
    assert res["goals"][0]["months_remaining"] == 5
    assert res["goals"][1]["months_remaining"] == -1 # Stalled
    assert res["goals"][2]["probability"] == 100.0

@pytest.mark.asyncio
async def test_planning_engine():
    mock_db = AsyncMock()
    engine = WealthPlanningEngine(mock_db)
    
    # We can mock the sub-engines directly to avoid huge mocks
    engine.networth_engine.calculate_net_worth = AsyncMock(return_value={
        "total_assets": 100000.0,
        "total_liabilities": 20000.0,
        "assets": {"cash": 20000.0, "investments": 80000.0}
    })
    
    engine.cashflow_engine.calculate_monthly_cashflow = AsyncMock(return_value={
        "total_income": 10000.0,
        "total_expenses": 5000.0,
        "savings_rate_percentage": 50.0
    })
    
    res = await engine.calculate_wealth_plan(1)
    
    assert res["emergency_fund_coverage_months"] == 4.0 # 20000 / 5000
    assert res["savings_ratio_percentage"] == 50.0
    assert res["investment_ratio_percentage"] == 80.0
    
    # Financial score calculation check
    # Base 50
    # +10 (EF > 3)
    # +15 (DTI: 20000 * 0.03 / 10000 = 6% < 30%)
    # +15 (Savings > 20%)
    # Total = 90
    assert res["financial_health_score"] == 90

@pytest.mark.asyncio
async def test_goals_engine_edge_cases():
    mock_db = AsyncMock()
    engine = GoalEngine(mock_db)
    
    # Negative contribution
    mock_goal_neg = MagicMock()
    mock_goal_neg.target_amount = 10000.0
    mock_goal_neg.current_progress = 5000.0
    mock_goal_neg.monthly_contribution = -100.0
    mock_goal_neg.estimated_completion_date = None
    mock_goal_neg.probability = 0.0
    
    # Target amount zero
    mock_goal_zero_target = MagicMock()
    mock_goal_zero_target.target_amount = 0.0
    mock_goal_zero_target.current_progress = 0.0
    mock_goal_zero_target.monthly_contribution = 100.0
    mock_goal_zero_target.estimated_completion_date = None
    mock_goal_zero_target.probability = 0.0
    
    # Overfunded
    mock_goal_over = MagicMock()
    mock_goal_over.target_amount = 5000.0
    mock_goal_over.current_progress = 6000.0
    mock_goal_over.monthly_contribution = 100.0
    mock_goal_over.estimated_completion_date = None
    mock_goal_over.probability = 0.0
    
    # Past target date (impossible)
    mock_goal_past = MagicMock()
    mock_goal_past.target_amount = 5000.0
    mock_goal_past.current_progress = 1000.0
    mock_goal_past.monthly_contribution = 10.0
    from datetime import timedelta
    mock_goal_past.estimated_completion_date = datetime.now(timezone.utc) - timedelta(days=30)
    mock_goal_past.probability = 0.0
    
    # Goal on track (high probability)
    mock_goal_ontrack = MagicMock()
    mock_goal_ontrack.target_amount = 5000.0
    mock_goal_ontrack.current_progress = 1000.0
    mock_goal_ontrack.monthly_contribution = 1000.0
    mock_goal_ontrack.estimated_completion_date = datetime.now(timezone.utc) + timedelta(days=150) # 5 months
    mock_goal_ontrack.probability = 0.0

    mock_res = MagicMock()
    mock_res.scalars.return_value.all.return_value = [
        mock_goal_neg, mock_goal_zero_target, mock_goal_over, mock_goal_past, mock_goal_ontrack
    ]
    mock_db.execute.return_value = mock_res
    
    res = await engine.calculate_goals_progress(1)
    
    assert res["total_goals"] == 5
    
    # Neg
    assert res["goals"][0]["months_remaining"] == -1
    
    # Zero target
    assert res["goals"][1]["progress_percentage"] == 0.0
    assert res["goals"][1]["months_remaining"] == 0
    assert res["goals"][1]["probability"] == 100.0
    
    # Overfunded
    assert res["goals"][2]["progress_percentage"] == 100.0
    assert res["goals"][2]["remaining_amount"] == -1000.0
    
    # Past target date (probability drops)
    assert res["goals"][3]["probability"] < 100.0
    
    # On track
    assert res["goals"][4]["probability"] >= 95.0

@pytest.mark.asyncio
async def test_planning_engine_edge_cases():
    mock_db = AsyncMock()
    engine = WealthPlanningEngine(mock_db)
    
    # Edge case 1: Zero income, zero expenses, zero investments
    engine.networth_engine.calculate_net_worth = AsyncMock(return_value={
        "total_assets": 0.0,
        "total_liabilities": 5000.0,
        "assets": {"cash": 0.0, "investments": 0.0}
    })
    
    engine.cashflow_engine.calculate_monthly_cashflow = AsyncMock(return_value={
        "total_income": 0.0,
        "total_expenses": 0.0,
        "savings_rate_percentage": 0.0
    })
    
    res = await engine.calculate_wealth_plan(1)
    assert res["emergency_fund_coverage_months"] == 0.0
    assert res["debt_to_income_ratio_percentage"] == 0.0
    assert res["investment_ratio_percentage"] == 0.0
    assert res["retirement_readiness"]["fire_target"] == 0.0
    
    # Edge case 2: Negative cash flow, high debt ratio, no emergency fund
    engine.networth_engine.calculate_net_worth = AsyncMock(return_value={
        "total_assets": 1000.0,
        "total_liabilities": 100000.0,
        "assets": {"cash": 100.0, "investments": 900.0}
    })
    
    engine.cashflow_engine.calculate_monthly_cashflow = AsyncMock(return_value={
        "total_income": 2000.0,
        "total_expenses": 3000.0,
        "savings_rate_percentage": -50.0
    })
    
    res2 = await engine.calculate_wealth_plan(1)
    assert res2["emergency_fund_coverage_months"] < 1.0
    assert res2["debt_to_income_ratio_percentage"] > 50.0
    assert res2["financial_health_score"] < 50
    
    # Edge case 3: FIRE achieved, extremely high savings rate
    engine.networth_engine.calculate_net_worth = AsyncMock(return_value={
        "total_assets": 2000000.0,
        "total_liabilities": 0.0,
        "assets": {"cash": 100000.0, "investments": 1900000.0}
    })
    
    engine.cashflow_engine.calculate_monthly_cashflow = AsyncMock(return_value={
        "total_income": 10000.0,
        "total_expenses": 4000.0,
        "savings_rate_percentage": 60.0
    })
    
    res3 = await engine.calculate_wealth_plan(1)
    assert res3["emergency_fund_coverage_months"] >= 6.0
    assert res3["financial_health_score"] == 100
    assert res3["retirement_readiness"]["fire_progress_percentage"] >= 100.0
