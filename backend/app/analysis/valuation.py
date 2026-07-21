import math
from typing import List, Optional
from app.market_data.models import IncomeStatement, BalanceSheet, CashFlowStatement, StockQuote
from app.analysis.models import ValuationMetrics, ForecastScenario

class ValuationEngine:
    """
    Computes intrinsic values using DCF, DDM, WACC, and CAPM.
    """
    
    def calculate_wacc(
        self,
        beta: float,
        risk_free_rate: float,
        market_return: float,
        total_debt: float,
        market_cap: float,
        interest_expense: float,
        tax_rate: float
    ) -> (float, float, float):
        """Returns (WACC, Cost of Equity, Cost of Debt)"""
        # CAPM: Ke = Rf + Beta * (Rm - Rf)
        cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
        
        # Kd = Interest Expense / Total Debt
        cost_of_debt = (interest_expense / total_debt) if total_debt > 0 else 0.0
        
        total_capital = market_cap + total_debt
        weight_equity = market_cap / total_capital if total_capital > 0 else 1.0
        weight_debt = total_debt / total_capital if total_capital > 0 else 0.0
        
        wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
        return wacc, cost_of_equity, cost_of_debt

    def dcf_valuation(
        self,
        base_case: ForecastScenario,
        wacc: float,
        terminal_growth_rate: float,
        shares_outstanding: float,
        total_debt: float,
        cash: float
    ) -> (float, float):
        """Returns (Intrinsic Value per Share, Enterprise Value)"""
        present_value_fcf = 0.0
        for i, point in enumerate(base_case.projections):
            # Discount Factor = (1 + WACC) ^ t
            discount_factor = math.pow(1 + wacc, i + 1)
            present_value_fcf += (point.fcf / discount_factor)
            
        last_fcf = base_case.projections[-1].fcf
        
        # Terminal Value = FCF_n * (1 + g) / (WACC - g)
        if wacc <= terminal_growth_rate:
            # Fallback if WACC is too low for the Gordon Growth Model
            terminal_value = last_fcf * 15 # Simple 15x multiple
        else:
            terminal_value = last_fcf * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)
            
        # Discount Terminal Value back to PV
        present_value_tv = terminal_value / math.pow(1 + wacc, len(base_case.projections))
        
        enterprise_value = present_value_fcf + present_value_tv
        equity_value = enterprise_value + cash - total_debt
        
        intrinsic_value = equity_value / shares_outstanding if shares_outstanding > 0 else 0.0
        return intrinsic_value, enterprise_value

    def calculate_ddm(self, current_dividend: float, cost_of_equity: float, dividend_growth_rate: float) -> Optional[float]:
        if current_dividend <= 0 or cost_of_equity <= dividend_growth_rate:
            return None
        return (current_dividend * (1 + dividend_growth_rate)) / (cost_of_equity - dividend_growth_rate)
        
    def generate_sensitivity_matrix(self, base_case: ForecastScenario, base_wacc: float, base_growth: float, shares_outstanding: float, total_debt: float, cash: float) -> dict:
        matrix = {}
        wacc_variations = [base_wacc - 0.02, base_wacc - 0.01, base_wacc, base_wacc + 0.01, base_wacc + 0.02]
        growth_variations = [base_growth - 0.01, base_growth - 0.005, base_growth, base_growth + 0.005, base_growth + 0.01]
        
        for w in wacc_variations:
            if w <= 0: continue
            row = {}
            for g in growth_variations:
                if w <= g: continue
                val, _ = self.dcf_valuation(base_case, w, g, shares_outstanding, total_debt, cash)
                row[f"{g*100:.1f}%"] = val
            if row:
                matrix[f"{w*100:.1f}%"] = row
        return matrix

    def compute(
        self,
        income_statements: List[IncomeStatement],
        balance_sheets: List[BalanceSheet],
        cash_flows: List[CashFlowStatement],
        quote: StockQuote,
        beta: float,
        forecasts: ForecastScenario,
        risk_free_rate: float = 0.04,  # e.g., 10-Year Treasury Yield
        market_return: float = 0.09,    # e.g., Historical S&P 500 return
        current_dividend: float = 0.0,
        dividend_growth_rate: float = 0.02,
        comparable_pe_ratio: Optional[float] = None,
        comparable_ev_ebitda: Optional[float] = None
    ) -> ValuationMetrics:
        
        inc = income_statements[0]
        bal = balance_sheets[0]
        
        # Tax Rate
        tax_rate = inc.income_tax_expense / inc.income_before_tax if inc.income_before_tax != 0 else 0.21
        if tax_rate < 0 or tax_rate > 1: tax_rate = 0.21
            
        market_cap = quote.market_cap if quote.market_cap else (quote.price * inc.weighted_average_shs_out if inc.weighted_average_shs_out else 0)
        
        wacc, cost_of_equity, cost_of_debt = self.calculate_wacc(
            beta=beta,
            risk_free_rate=risk_free_rate,
            market_return=market_return,
            total_debt=bal.total_debt,
            market_cap=market_cap,
            interest_expense=inc.interest_expense,
            tax_rate=tax_rate
        )
        
        terminal_growth_rate = 0.025 # Long-term GDP growth approx
        intrinsic_value, ev = self.dcf_valuation(
            base_case=forecasts,
            wacc=wacc,
            terminal_growth_rate=terminal_growth_rate,
            shares_outstanding=inc.weighted_average_shs_out,
            total_debt=bal.total_debt,
            cash=bal.cash_and_cash_equivalents
        )
        
        # Comparable Company Analysis
        comparable_value = None
        if comparable_pe_ratio and inc.eps > 0:
            comparable_value = inc.eps * comparable_pe_ratio
        elif comparable_ev_ebitda and inc.ebitda > 0 and inc.weighted_average_shs_out > 0:
            implied_ev = inc.ebitda * comparable_ev_ebitda
            implied_equity = implied_ev + bal.cash_and_cash_equivalents - bal.total_debt
            comparable_value = implied_equity / inc.weighted_average_shs_out

        ddm_value = self.calculate_ddm(current_dividend, cost_of_equity, dividend_growth_rate)
        
        sensitivity = self.generate_sensitivity_matrix(
            base_case=forecasts, base_wacc=wacc, base_growth=terminal_growth_rate,
            shares_outstanding=inc.weighted_average_shs_out, total_debt=bal.total_debt, cash=bal.cash_and_cash_equivalents
        )
        
        # Value Ranges based on sensitivity (if matrix exists), else +/- 15%
        if sensitivity and f"{wacc*100:.1f}%" in sensitivity:
            center_row = list(sensitivity[f"{wacc*100:.1f}%"].values())
            if center_row:
                fair_value_lower = min(center_row)
                fair_value_upper = max(center_row)
            else:
                fair_value_lower = intrinsic_value * 0.85
                fair_value_upper = intrinsic_value * 1.15
        else:
            fair_value_lower = intrinsic_value * 0.85
            fair_value_upper = intrinsic_value * 1.15
            
        margin_of_safety = 0.0
        if intrinsic_value > 0 and quote.price > 0:
            margin_of_safety = ((intrinsic_value - quote.price) / intrinsic_value) * 100.0

        return ValuationMetrics(
            dcf_intrinsic_value=intrinsic_value,
            margin_of_safety=margin_of_safety,
            wacc=wacc,
            cost_of_equity=cost_of_equity,
            cost_of_debt=cost_of_debt,
            terminal_value=ev - bal.cash_and_cash_equivalents + bal.total_debt, # approximate PV of TV
            ddm_intrinsic_value=ddm_value,
            enterprise_value=ev,
            fair_value_lower=fair_value_lower,
            fair_value_upper=fair_value_upper,
            comparable_company_value=comparable_value,
            sensitivity_matrix=sensitivity
        )
