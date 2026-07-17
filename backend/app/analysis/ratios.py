import math
from typing import List, Optional
from app.market_data.models import IncomeStatement, BalanceSheet, CashFlowStatement, StockQuote
from app.analysis.models import RatioMetrics

class RatioEngine:
    """
    Computes all financial ratios from raw statements.
    """
    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, periods: int) -> Optional[float]:
        if start_value <= 0 or end_value <= 0 or periods <= 0:
            return None
        return (math.pow(end_value / start_value, 1.0 / periods) - 1.0) * 100.0

    def compute(
        self,
        income_statements: List[IncomeStatement],
        balance_sheets: List[BalanceSheet],
        cash_flows: List[CashFlowStatement],
        quote: StockQuote
    ) -> RatioMetrics:
        if not income_statements or not balance_sheets or not cash_flows or not quote:
            raise ValueError("Incomplete data provided to RatioEngine")

        # Use most recent period
        inc = income_statements[0]
        bal = balance_sheets[0]
        cf = cash_flows[0]
        
        # Safe divide helper
        def safe_div(n: float, d: float) -> float:
            return n / d if d and d != 0 else 0.0

        # Liquidity
        current_ratio = safe_div(bal.total_current_assets, bal.total_current_liabilities)
        quick_ratio = safe_div(bal.total_current_assets - bal.inventory, bal.total_current_liabilities)
        cash_ratio = safe_div(bal.cash_and_cash_equivalents, bal.total_current_liabilities)

        # Profitability (converted to percentages)
        gross_margin = safe_div(inc.gross_profit, inc.revenue) * 100.0
        operating_margin = safe_div(inc.operating_income, inc.revenue) * 100.0
        net_margin = safe_div(inc.net_income, inc.revenue) * 100.0
        roa = safe_div(inc.net_income, bal.total_assets) * 100.0
        roe = safe_div(inc.net_income, bal.total_stockholders_equity) * 100.0
        
        # ROIC = NOPAT / Invested Capital
        # NOPAT = Operating Income * (1 - Tax Rate) -> Approx tax rate
        tax_rate = safe_div(inc.income_tax_expense, inc.income_before_tax)
        if tax_rate < 0 or tax_rate > 1: tax_rate = 0.21 # fallback
        nopat = inc.operating_income * (1 - tax_rate)
        invested_capital = bal.total_debt + bal.total_stockholders_equity - bal.cash_and_cash_equivalents
        roic = safe_div(nopat, invested_capital) * 100.0

        # Leverage
        debt_to_equity = safe_div(bal.total_debt, bal.total_stockholders_equity)
        debt_ratio = safe_div(bal.total_debt, bal.total_assets)
        interest_coverage = safe_div(inc.operating_income, inc.interest_expense)

        # Efficiency
        asset_turnover = safe_div(inc.revenue, bal.total_assets)
        inventory_turnover = safe_div(inc.cost_of_revenue, bal.inventory)
        receivables_turnover = safe_div(inc.revenue, bal.net_receivables)

        # Valuation
        market_cap = quote.market_cap if quote.market_cap else (quote.price * inc.weighted_average_shs_out if inc.weighted_average_shs_out else 0.0)
        enterprise_value = market_cap + bal.total_debt - bal.cash_and_cash_equivalents
        
        pe_ratio = safe_div(quote.price, inc.eps) if inc.eps > 0 else 0.0
        ev_to_ebitda = safe_div(enterprise_value, inc.ebitda) if inc.ebitda > 0 else 0.0
        ev_to_sales = safe_div(enterprise_value, inc.revenue)
        price_to_book = safe_div(market_cap, bal.total_stockholders_equity)
        price_to_sales = safe_div(market_cap, inc.revenue)

        # Growth (3-year CAGR if 4 statements available, i.e., T=0,1,2,3)
        rev_cagr = eps_cagr = fcf_cagr = None
        if len(income_statements) >= 4 and len(cash_flows) >= 4:
            inc_old = income_statements[3]
            cf_old = cash_flows[3]
            rev_cagr = self.calculate_cagr(inc_old.revenue, inc.revenue, 3)
            # Handle negative to positive EPS carefully, simplified for now
            eps_cagr = self.calculate_cagr(inc_old.eps, inc.eps, 3)
            fcf_cagr = self.calculate_cagr(cf_old.free_cash_flow, cf.free_cash_flow, 3)
            
        peg_ratio = None
        if pe_ratio > 0 and eps_cagr and eps_cagr > 0:
            peg_ratio = pe_ratio / eps_cagr

        return RatioMetrics(
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            cash_ratio=cash_ratio,
            gross_margin=gross_margin,
            operating_margin=operating_margin,
            net_margin=net_margin,
            return_on_assets=roa,
            return_on_equity=roe,
            return_on_invested_capital=roic,
            debt_to_equity=debt_to_equity,
            debt_ratio=debt_ratio,
            interest_coverage=interest_coverage,
            asset_turnover=asset_turnover,
            inventory_turnover=inventory_turnover,
            receivables_turnover=receivables_turnover,
            pe_ratio=pe_ratio,
            peg_ratio=peg_ratio,
            ev_to_ebitda=ev_to_ebitda,
            ev_to_sales=ev_to_sales,
            price_to_book=price_to_book,
            price_to_sales=price_to_sales,
            revenue_cagr_3y=rev_cagr,
            eps_cagr_3y=eps_cagr,
            fcf_cagr_3y=fcf_cagr
        )
