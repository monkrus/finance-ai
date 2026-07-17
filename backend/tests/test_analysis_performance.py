import pytest
import math
from app.analysis.ratios import RatioEngine
from app.analysis.valuation import ValuationEngine
from tests.test_analysis_edge_cases import get_base_statements
from app.analysis.models import ForecastScenario, ForecastPoint

def test_ratio_engine_performance(benchmark):
    inc, bal, cf, quote = get_base_statements()
    engine = RatioEngine()
    
    # Benchmark the compute function
    result = benchmark(engine.compute, [inc], [bal], [cf], quote)
    assert result is not None
    assert result.current_ratio > 0

def test_valuation_engine_performance(benchmark):
    inc, bal, cf, quote = get_base_statements()
    engine = ValuationEngine()
    
    forecasts = ForecastScenario(scenario_name="Base", cagr_assumptions={}, projections=[
        ForecastPoint(year=2025, revenue=1100, eps=3.3, fcf=330.0, operating_margin=0.4),
        ForecastPoint(year=2026, revenue=1210, eps=3.63, fcf=363.0, operating_margin=0.4),
        ForecastPoint(year=2027, revenue=1331, eps=3.99, fcf=399.0, operating_margin=0.4),
        ForecastPoint(year=2028, revenue=1464, eps=4.39, fcf=439.0, operating_margin=0.4),
        ForecastPoint(year=2029, revenue=1610, eps=4.83, fcf=483.0, operating_margin=0.4)
    ])
    
    # Benchmark the compute function
    result = benchmark(engine.compute, [inc], [bal], [cf], quote, 1.0, forecasts)
    assert result is not None
    assert result.wacc > 0
