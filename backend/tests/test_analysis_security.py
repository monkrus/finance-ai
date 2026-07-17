import pytest
from app.analysis.ratios import RatioEngine
from tests.test_analysis_edge_cases import get_base_statements

def test_float_overflow_protection():
    inc, bal, cf, quote = get_base_statements()
    
    # Extreme revenue to test overflow/inf handling
    inc.revenue = 1e308
    inc.net_income = 1e308
    bal.total_assets = 1e308
    
    engine = RatioEngine()
    try:
        ratios = engine.compute([inc], [bal], [cf], quote)
        assert ratios is not None
    except OverflowError:
        pytest.fail("RatioEngine failed to handle float overflow gracefully.")

def test_invalid_api_input():
    # If the API returns None or missing objects, standard Pydantic models will fail at the edge, 
    # but let's test if the engine can handle zero'd or empty structures
    inc, bal, cf, quote = get_base_statements()
    inc.revenue = -1 # Invalid state logically
    engine = RatioEngine()
    
    ratios = engine.compute([inc], [bal], [cf], quote)
    # Shouldn't crash, should just return weird numbers or 0.
    assert ratios is not None
