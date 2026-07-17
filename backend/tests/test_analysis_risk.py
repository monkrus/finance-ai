import pytest
import math
from app.analysis.risk import RiskEngine
from app.market_data.models import HistoricalPriceSeries, HistoricalPrice

def test_risk_engine_math():
    engine = RiskEngine()
    
    asset_prices = [100, 105, 102, 108, 110]
    market_prices = [1000, 1020, 1010, 1040, 1050]
    
    asset_history = HistoricalPriceSeries(
        ticker="ASSET",
        prices=[
            HistoricalPrice(date="1", open=p, high=p, low=p, close=p, volume=100) for p in asset_prices
        ]
    )
    
    market_history = HistoricalPriceSeries(
        ticker="SPY",
        prices=[
            HistoricalPrice(date="1", open=p, high=p, low=p, close=p, volume=100) for p in market_prices
        ]
    )
    
    risk = engine.compute(asset_history, market_history, risk_free_rate=0.0)
    
    assert risk.beta > 0
    assert risk.volatility > 0
    assert risk.correlation_to_market > 0
    
    # Max drawdown is from 105 down to 102: 3/105 = 0.02857
    assert round(risk.max_drawdown, 4) == round(3.0 / 105.0, 4)
