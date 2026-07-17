import pytest
from app.ai.metrics import MetricsTracker

def test_metrics_tracker():
    tracker = MetricsTracker()
    tracker.track("gemini-2.5-flash", tokens=1500, latency_ms=450.5)
    
    assert tracker.total_tokens == 1500
    assert tracker.total_cost == pytest.approx(0.00015)
    
    tracker.track_tool_call("get_price", latency_ms=100.0)
    assert tracker.tool_calls == 1
