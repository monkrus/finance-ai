import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsTracker:
    """
    Tracks AI usage, token consumption, latency, and estimates cost.
    """
    def __init__(self):
        self.total_tokens: int = 0
        self.total_cost: float = 0.0
        self.tool_calls: int = 0
        
        self.COST_PER_1K = {
            "gemini-2.5-flash": 0.0001
        }
        
    def track_tool_call(self, name: str, latency_ms: float):
        self.tool_calls += 1
        logger.info(f"AI Metrics | Tool Call: {name} | Latency: {latency_ms:.2f}ms")
        
    def track(self, model: str, tokens: int, latency_ms: float):
        self.total_tokens += tokens
        cost_rate = self.COST_PER_1K.get(model, 0.0)
        cost = (tokens / 1000.0) * cost_rate
        self.total_cost += cost
        
        logger.info(
            f"AI Metrics | Model: {model} | Tokens: {tokens} | "
            f"Cost: ${cost:.6f} | Latency: {latency_ms:.2f}ms"
        )
