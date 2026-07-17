from typing import List
from collections import defaultdict
import math
from app.schemas.portfolio import Holding, AllocationMetrics

class AllocationEngine:
    """
    Computes diversification and concentration metrics.
    """
    
    def compute(self, holdings: List[Holding], total_value: float) -> AllocationMetrics:
        if total_value <= 0:
            return AllocationMetrics(
                asset_allocation={}, sector_allocation={}, industry_allocation={}, 
                country_allocation={}, currency_allocation={}, top_holdings=[], diversification_score=0.0
            )

        asset_alloc = defaultdict(float)
        sector_alloc = defaultdict(float)
        industry_alloc = defaultdict(float)
        country_alloc = defaultdict(float)
        currency_alloc = defaultdict(float)
        
        for h in holdings:
            if h.market_value is None or h.market_value <= 0:
                continue
                
            weight = h.market_value / total_value
            
            asset_alloc[h.asset_type] += weight
            sector_alloc[h.sector or "Unknown"] += weight
            industry_alloc[h.industry or "Unknown"] += weight
            country_alloc[h.country or "Unknown"] += weight
            currency_alloc[h.currency or "USD"] += weight
            
        # Top Holdings
        sorted_holdings = sorted([h for h in holdings if h.market_value], key=lambda x: x.market_value, reverse=True)
        top_holdings = [{"ticker": h.ticker_symbol, "weight": (h.market_value/total_value)*100} for h in sorted_holdings[:10]]
        
        # Diversification Score (Herfindahl-Hirschman Index inverse approximation)
        hhi = sum(math.pow(h.market_value / total_value, 2) for h in holdings if h.market_value)
        div_score = max(0, 100.0 - (hhi * 100.0))
        
        return AllocationMetrics(
            asset_allocation=dict(asset_alloc),
            sector_allocation=dict(sector_alloc),
            industry_allocation=dict(industry_alloc),
            country_allocation=dict(country_alloc),
            currency_allocation=dict(currency_alloc),
            top_holdings=top_holdings,
            diversification_score=div_score
        )
