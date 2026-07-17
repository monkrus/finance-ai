import math
from typing import List, Dict, Optional
from app.market_data.models import IncomeStatement, CashFlowStatement
from app.analysis.models import ForecastPoint, ForecastScenario, ForecastingMetrics

class ForecastingEngine:
    """
    Extrapolates Revenue, EPS, FCF, and Margins for Bull, Base, and Bear scenarios.
    """
    
    def _calculate_cagr(self, start: float, end: float, periods: int) -> float:
        if start <= 0 or end <= 0 or periods <= 0:
            return 0.05 # Default 5% if impossible
        return math.pow(end / start, 1.0 / periods) - 1.0

    def generate_scenario(
        self,
        name: str,
        current_year: int,
        latest_rev: float,
        latest_eps: float,
        latest_fcf: float,
        latest_margin: float,
        rev_growth: float,
        eps_growth: float,
        fcf_growth: float,
        margin_change: float,
        years: int = 5
    ) -> ForecastScenario:
        
        points = []
        rev, eps, fcf, margin = latest_rev, latest_eps, latest_fcf, latest_margin
        
        for i in range(1, years + 1):
            rev = rev * (1 + rev_growth)
            eps = eps * (1 + eps_growth)
            fcf = fcf * (1 + fcf_growth)
            margin = margin + margin_change # additive basis points
            
            points.append(ForecastPoint(
                year=current_year + i,
                revenue=rev,
                eps=eps,
                fcf=fcf,
                operating_margin=margin
            ))
            
        return ForecastScenario(
            scenario_name=name,
            cagr_assumptions={
                "revenue": rev_growth,
                "eps": eps_growth,
                "fcf": fcf_growth,
                "margin_change": margin_change
            },
            projections=points
        )

    def compute(
        self,
        income_statements: List[IncomeStatement],
        cash_flows: List[CashFlowStatement],
        forecast_years: int = 5
    ) -> ForecastingMetrics:
        
        inc = income_statements[0]
        cf = cash_flows[0]
        
        # Determine historical CAGRs (if enough data)
        rev_cagr = 0.05
        eps_cagr = 0.05
        fcf_cagr = 0.05
        
        if len(income_statements) >= 4 and len(cash_flows) >= 4:
            inc_old = income_statements[3]
            cf_old = cash_flows[3]
            rev_cagr = self._calculate_cagr(inc_old.revenue, inc.revenue, 3)
            eps_cagr = self._calculate_cagr(inc_old.eps, inc.eps, 3)
            fcf_cagr = self._calculate_cagr(cf_old.free_cash_flow, cf.free_cash_flow, 3)
            
        # Bound extreme CAGRs (e.g. don't project 200% growth forever)
        rev_cagr = max(0.0, min(rev_cagr, 0.30))
        eps_cagr = max(0.0, min(eps_cagr, 0.35))
        fcf_cagr = max(0.0, min(fcf_cagr, 0.35))
        
        current_year = int(inc.calendar_year) if inc.calendar_year.isdigit() else 2024
        
        latest_margin = inc.operating_income_ratio if hasattr(inc, 'operating_income_ratio') else (inc.operating_income / inc.revenue if inc.revenue > 0 else 0)

        # Base Case = Historical trends fading slightly
        base = self.generate_scenario(
            name="Base",
            current_year=current_year,
            latest_rev=inc.revenue,
            latest_eps=inc.eps,
            latest_fcf=cf.free_cash_flow,
            latest_margin=latest_margin,
            rev_growth=rev_cagr * 0.9,
            eps_growth=eps_cagr * 0.9,
            fcf_growth=fcf_cagr * 0.9,
            margin_change=0.005, # +0.5% margin expansion per year
            years=forecast_years
        )
        
        # Bull Case = Accelerated growth
        bull = self.generate_scenario(
            name="Bull",
            current_year=current_year,
            latest_rev=inc.revenue,
            latest_eps=inc.eps,
            latest_fcf=cf.free_cash_flow,
            latest_margin=latest_margin,
            rev_growth=rev_cagr * 1.2,
            eps_growth=eps_cagr * 1.2,
            fcf_growth=fcf_cagr * 1.2,
            margin_change=0.015, # +1.5% margin expansion
            years=forecast_years
        )
        
        # Bear Case = Decelerated/Stagnant growth
        bear = self.generate_scenario(
            name="Bear",
            current_year=current_year,
            latest_rev=inc.revenue,
            latest_eps=inc.eps,
            latest_fcf=cf.free_cash_flow,
            latest_margin=latest_margin,
            rev_growth=rev_cagr * 0.4,
            eps_growth=eps_cagr * 0.4,
            fcf_growth=fcf_cagr * 0.4,
            margin_change=-0.01, # -1.0% margin compression
            years=forecast_years
        )
        
        return ForecastingMetrics(
            bull_case=bull,
            base_case=base,
            bear_case=bear
        )
