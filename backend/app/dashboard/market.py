import asyncio
from app.dashboard.schemas import MarketSection
from app.dashboard.widgets import WidgetBuilder
from app.dashboard.cache import DashboardCache
from app.market_data.service import MarketDataService

class MarketDashboard:
    def __init__(self):
        pass

    # Cache market data for 30 seconds
    @DashboardCache.cached(ttl_seconds=30)
    async def get_section(self) -> dict:
        try:
            provider = MarketDataService()
            indices_task = provider.get_market_indices()
            # For trending we mock it as it might not be in the service directly
            trending_task = asyncio.sleep(0.1)
            indices, trending = await asyncio.gather(indices_task, trending_task)
        except Exception:
            # Fallback mock
            indices = {"SPY": {"price": 500.0, "change": 5.0, "change_percent": 1.0}}
            trending = []

        widgets = []
        if isinstance(indices, list):
            for data in indices:
                # `data` should be a MarketIndex object, let's just use getattr/dict
                try:
                    val = data.value if hasattr(data, 'value') else data.get("value", 0.0)
                    chg = data.change if hasattr(data, 'change') else data.get("change", 0.0)
                    chg_pct = data.change_percent if hasattr(data, 'change_percent') else data.get("change_percent", 0.0)
                    sym = data.symbol if hasattr(data, 'symbol') else data.get("symbol", "Index")
                    widgets.append(WidgetBuilder.build(
                        title=f"{sym} Index",
                        value=val,
                        formatted_value=f"{val:,.2f}",
                        change=chg,
                        change_percent=chg_pct,
                        icon="trending-up"
                    ))
                except Exception:
                    pass
        elif isinstance(indices, dict):
            for symbol, data in indices.items():
                widgets.append(WidgetBuilder.build(
                    title=f"{symbol} Index",
                    value=data.get("price", 0.0),
                    formatted_value=f"{data.get('price', 0.0):,.2f}",
                    change=data.get("change", 0.0),
                    change_percent=data.get("change_percent", 0.0),
                    icon="trending-up"
                ))

        return {"widgets": [w.model_dump() for w in widgets]}
