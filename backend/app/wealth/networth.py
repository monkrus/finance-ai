from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.wealth import Account, AccountType
from app.models.portfolio import Portfolio, Holding

class NetWorthEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_net_worth(self, user_id: int) -> dict:
        # Get all personal finance accounts
        result = await self.db.execute(select(Account).where(Account.user_id == user_id))
        accounts = result.scalars().all()

        # Calculate basic assets and liabilities
        total_cash = 0.0
        total_liabilities = 0.0
        asset_breakdown = {}
        liability_breakdown = {}

        for acc in accounts:
            if acc.account_type in [AccountType.CASH, AccountType.SAVINGS, AccountType.CURRENT]:
                total_cash += acc.balance
                asset_breakdown[acc.name] = acc.balance
            elif acc.account_type in [AccountType.CREDIT_CARD, AccountType.LOAN]:
                total_liabilities += acc.balance
                liability_breakdown[acc.name] = acc.balance

        # Integrate with Portfolio Module (Module 7) for investments
        port_result = await self.db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        portfolios = port_result.scalars().all()
        
        total_investments = 0.0
        investment_breakdown = {}
        
        for port in portfolios:
            # Reconstruct portfolio value (simplification for real-time net worth)
            # In a real scenario, we might use a historical snapshot or external price service
            # Here we just sum the current values of holdings if available
            port_val = 0.0
            holdings_res = await self.db.execute(select(Holding).where(Holding.portfolio_id == port.id))
            holdings = holdings_res.scalars().all()
            for h in holdings:
                # We assume cost_basis approximates current value if live prices are unavailable
                port_val += h.cost_basis 
            
            total_investments += port_val
            investment_breakdown[port.name] = port_val

        total_assets = total_cash + total_investments
        net_worth = total_assets - total_liabilities

        return {
            "net_worth": net_worth,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "assets": {
                "cash": total_cash,
                "investments": total_investments,
                "cash_accounts": asset_breakdown,
                "investment_portfolios": investment_breakdown
            },
            "liabilities": liability_breakdown,
            "asset_allocation": {
                "cash_pct": (total_cash / total_assets * 100) if total_assets > 0 else 0,
                "investments_pct": (total_investments / total_assets * 100) if total_assets > 0 else 0
            }
        }
