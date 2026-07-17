import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.news.sentiment import SentimentEngine
from app.news.extraction import EntityEngine, EventEngine
from app.news.summarization import SummarizationEngine
from app.news.impact import PortfolioImpactEngine

@pytest.fixture
def mock_gateway():
    with patch("app.news.sentiment.AIGatewayService") as mock_gw:
        yield mock_gw

@pytest.mark.asyncio
async def test_sentiment_engine():
    with patch("app.news.sentiment.AIGatewayService") as MockGW:
        mock_instance = MockGW.return_value
        mock_instance.chat = AsyncMock(return_value='{"label": "Positive", "score": 0.8, "confidence": 0.9, "reasoning": "Good"}')
        
        engine = SentimentEngine()
        res = await engine.analyze("Headline", "Content")
        
        assert res is not None
        assert res.label == "Positive"
        assert res.score == 0.8

@pytest.mark.asyncio
async def test_entity_engine():
    with patch("app.news.extraction.AIGatewayService") as MockGW:
        mock_instance = MockGW.return_value
        mock_instance.chat = AsyncMock(return_value='[{"entity_type": "Company", "entity_name": "Apple"}]')
        
        engine = EntityEngine()
        res = await engine.extract("Headline", "Content")
        
        assert len(res) == 1
        assert res[0].entity_name == "Apple"

@pytest.mark.asyncio
async def test_event_engine():
    with patch("app.news.extraction.AIGatewayService") as MockGW:
        mock_instance = MockGW.return_value
        mock_instance.chat = AsyncMock(return_value='[{"event_type": "Earnings", "details": {"Q1": "Beat"}}]')
        
        engine = EventEngine()
        res = await engine.detect("Headline", "Content")
        
        assert len(res) == 1
        assert res[0].event_type == "Earnings"

@pytest.mark.asyncio
async def test_summary_engine():
    with patch("app.news.summarization.AIGatewayService") as MockGW:
        mock_instance = MockGW.return_value
        mock_instance.chat = AsyncMock(return_value='{"executive_summary": "Sum", "key_takeaways": ["1"], "bullish_signals": [], "bearish_signals": [], "opportunities": [], "risks": [], "market_impact": "None"}')
        
        engine = SummarizationEngine()
        res = await engine.summarize("Headline", "Content")
        
        assert res is not None
        assert res.executive_summary == "Sum"

@pytest.mark.asyncio
async def test_portfolio_impact_engine():
    mock_db = AsyncMock()
    
    # Mock portfolios
    mock_port = MagicMock()
    mock_port.id = 1
    
    # Mock holdings
    mock_hold = MagicMock()
    mock_hold.ticker_symbol = "AAPL"
    mock_hold.cost_basis = 1000.0
    
    def make_side_effects():
        mock_port_res = MagicMock()
        mock_port_res.scalars().all.return_value = [mock_port]
        mock_hold_res = MagicMock()
        mock_hold_res.scalars().all.return_value = [mock_hold]
        return [mock_port_res, mock_hold_res]
    
    engine = PortfolioImpactEngine(mock_db)
    
    from app.schemas.news import NewsEntitySchema, NewsEventSchema
    entities = [NewsEntitySchema(entity_type="Ticker", entity_name="AAPL")]
    
    mock_db.execute.side_effect = make_side_effects()
    impacts = await engine.determine_impact(1, entities, [], 0.5)
    assert len(impacts) == 1
    assert impacts[0].portfolio_id == 1
    assert "AAPL" in impacts[0].affected_holdings
    assert impacts[0].alert_priority in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # Test high priority
    mock_db.execute.side_effect = make_side_effects()
    impacts2 = await engine.determine_impact(1, entities, [], 0.5, importance_score=85)
    assert impacts2[0].alert_priority == "CRITICAL"
    
    mock_db.execute.side_effect = make_side_effects()
    impacts3 = await engine.determine_impact(1, entities, [], 0.5, importance_score=65)
    assert impacts3[0].alert_priority == "HIGH"
    
    mock_db.execute.side_effect = make_side_effects()
    impacts4 = await engine.determine_impact(1, entities, [], 0.5, importance_score=45)
    assert impacts4[0].alert_priority == "MEDIUM"
