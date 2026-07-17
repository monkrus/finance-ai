from app.ai.tool_registry import ToolRegistry
from app.ai.models import AITool
from app.market_data.service import MarketDataService
from app.document_intelligence.engine import RAGEngine
import logging

logger = logging.getLogger(__name__)

def evaluate_math(expression: str) -> str:
    """A safe, basic math evaluator."""
    import ast
    import operator
    
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    def eval_expr(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant: {node.value}")
        elif isinstance(node, ast.BinOp):
            return allowed_operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return allowed_operators[type(node.op)](eval_expr(node.operand))
        else:
            raise TypeError(node)

    try:
        node = ast.parse(expression, mode='eval').body
        return str(eval_expr(node))
    except Exception as e:
        return f"Math Evaluation Error: {str(e)}"

def register_all_tools(registry: ToolRegistry, md_service: MarketDataService, rag_engine: RAGEngine = None):
    
    # 1. Math Calculator
    calc_tool = AITool(
        name="calculator",
        description="Evaluate basic mathematical expressions. Supports addition, subtraction, multiplication, division, and exponents.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression (e.g., '100 * 1.05 ** 10')"
                }
            },
            "required": ["expression"]
        }
    )
    async def calc_callback(expression: str):
        return evaluate_math(expression)
        
    registry.register(calc_tool, calc_callback)

    # 2. Company Profile
    profile_tool = AITool(
        name="get_company_profile",
        description="Get company profile and description by ticker symbol.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"]
        }
    )
    async def profile_cb(ticker: str):
        prof = await md_service.get_company_profile(ticker)
        return prof.model_dump() if prof else {"error": "Not found"}
    registry.register(profile_tool, profile_cb)

    # 3. Stock Quote
    quote_tool = AITool(
        name="get_stock_quote",
        description="Get real-time stock quote and price.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"]
        }
    )
    async def quote_cb(ticker: str):
        quote = await md_service.get_quote(ticker)
        return quote.model_dump() if quote else {"error": "Not found"}
    registry.register(quote_tool, quote_cb)

    # 4. Market News
    news_tool = AITool(
        name="get_market_news",
        description="Get latest market news for a ticker.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "limit": {"type": "integer", "description": "Number of articles"}
            },
            "required": ["ticker"]
        }
    )
    async def news_cb(ticker: str, limit: int = 5):
        news = await md_service.get_market_news(ticker, limit)
        return [n.model_dump() for n in news]
    registry.register(news_tool, news_cb)

    # 5. Financial Ratios
    ratios_tool = AITool(
        name="get_financial_ratios",
        description="Get key financial ratios (P/E, ROE, Debt/Equity, etc).",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"]
        }
    )
    async def ratios_cb(ticker: str):
        ratios = await md_service.get_financial_ratios(ticker)
        return [r.model_dump() for r in ratios]
    registry.register(ratios_tool, ratios_cb)
    
    # 6. RAG Document Query
    if rag_engine:
        rag_tool = AITool(
            name="query_financial_documents",
            description="Query uploaded financial documents (e.g. 10-K, Earnings Calls) to answer complex financial questions with citations.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "ticker": {"type": "string"}
                },
                "required": ["query"]
            }
        )
        async def rag_cb(query: str, ticker: str = None):
            filters = {"ticker": ticker} if ticker else None
            resp = await rag_engine.query(query, top_k=5, metadata_filters=filters)
            return resp.model_dump()
        registry.register(rag_tool, rag_cb)

    # 7. Comprehensive Financial Analysis
    analysis_tool = AITool(
        name="run_financial_analysis",
        description="Run a full quantitative analysis on a company, generating intrinsic valuation, risk metrics, financial scoring, and financial forecasts.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"]
        }
    )
    async def analysis_cb(ticker: str):
        from app.analysis.engine import AnalysisEngine
        try:
            engine = AnalysisEngine(market_data_service=md_service)
            report = await engine.generate_full_report(ticker)
            return report.model_dump()
        except Exception as e:
            return {"error": str(e)}
    registry.register(analysis_tool, analysis_cb)
        
    # 8. Portfolio Analytics (Comprehensive)
    portfolio_tool = AITool(
        name="analyze_portfolio",
        description="Run comprehensive analytics on a user's portfolio including performance metrics, asset allocation, and risk metrics.",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def portfolio_cb(portfolio_id: int):
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return analytics.model_dump()
        except Exception as e:
            return {"error": str(e)}
            
    registry.register(portfolio_tool, portfolio_cb)
    
    # 9. Portfolio Summary
    portfolio_summary_tool = AITool(
        name="portfolio_summary",
        description="Get a high-level summary of a user's portfolio.",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def summary_cb(portfolio_id: int):
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return {"portfolio_value": analytics.performance.portfolio_value, "total_return_pct": analytics.performance.total_return_pct}
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_summary_tool, summary_cb)

    # 10. Portfolio Risk
    portfolio_risk_tool = AITool(
        name="portfolio_risk",
        description="Analyze the risk metrics of a portfolio (Beta, Volatility).",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def prisk_cb(portfolio_id: int):
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return analytics.risk.model_dump()
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_risk_tool, prisk_cb)
    
    # 11. Portfolio Allocation
    portfolio_alloc_tool = AITool(
        name="portfolio_allocation",
        description="Analyze the allocation of a portfolio (Sector, Industry, Asset Class).",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def alloc_cb(portfolio_id: int):
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return analytics.allocation.model_dump()
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_alloc_tool, alloc_cb)
    
    # 12. Portfolio Performance
    portfolio_perf_tool = AITool(
        name="portfolio_performance",
        description="Analyze the performance returns of a portfolio.",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def pperf_cb(portfolio_id: int):
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return analytics.performance.model_dump()
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_perf_tool, pperf_cb)

    # 13. Portfolio Recommendations
    portfolio_rec_tool = AITool(
        name="portfolio_recommendations",
        description="Get AI investment recommendations to optimize a portfolio based on its current risk and allocation.",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def prec_cb(portfolio_id: int):
        # Recommendations is primarily a function of the LLM analyzing the analytics output. 
        # This tool returns the analytics and a prompt hint to the agent.
        from app.portfolio.engine import PortfolioEngine
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioEngine(market_data_service=md_service)
                analytics = await engine.get_portfolio_analytics(db, portfolio_id)
                return {
                    "data": analytics.model_dump(), 
                    "instructions": "Use this analytics data to generate portfolio balancing recommendations."
                }
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_rec_tool, prec_cb)
        
    # 14. Company News
    company_news_tool = AITool(
        name="company_news",
        description="Get the latest news articles for a specific company ticker.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"]
        }
    )
    async def company_news_cb(ticker: str):
        from sqlalchemy.future import select
        from app.models.news import NewsArticle, NewsEntity
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                res = await db.execute(
                    select(NewsArticle).join(NewsArticle.entities).where(NewsEntity.entity_name == ticker.upper()).order_by(NewsArticle.published_at.desc()).limit(5)
                )
                articles = res.scalars().all()
                return [{"headline": a.headline, "summary": a.content, "url": a.source_url} for a in articles]
        except Exception as e:
            return {"error": str(e)}
    registry.register(company_news_tool, company_news_cb)

    # 15. Market Sentiment
    market_sentiment_tool = AITool(
        name="market_sentiment",
        description="Get the overall market sentiment or sentiment for a specific ticker based on recent news.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Optional ticker to filter sentiment."}
            }
        }
    )
    async def market_sentiment_cb(ticker: str = None):
        from sqlalchemy.future import select
        from app.models.news import NewsArticle, NewsEntity, NewsSentiment
        from app.core.database import AsyncSessionLocal
        try:
            async with AsyncSessionLocal() as db:
                query = select(NewsSentiment).join(NewsSentiment.article)
                if ticker:
                    query = query.join(NewsArticle.entities).where(NewsEntity.entity_name == ticker.upper())
                query = query.order_by(NewsArticle.published_at.desc()).limit(10)
                res = await db.execute(query)
                sentiments = res.scalars().all()
                if not sentiments:
                    return {"sentiment": "Neutral", "score": 0.0}
                avg_score = sum(s.score for s in sentiments) / len(sentiments)
                label = "Positive" if avg_score > 0.2 else ("Negative" if avg_score < -0.2 else "Neutral")
                return {"sentiment": label, "average_score": avg_score, "analyzed_articles": len(sentiments)}
        except Exception as e:
            return {"error": str(e)}
    registry.register(market_sentiment_tool, market_sentiment_cb)
    
    # 16. Portfolio News
    portfolio_news_tool = AITool(
        name="portfolio_news",
        description="Get news impacts related to a user's portfolio.",
        parameters={
            "type": "object",
            "properties": {
                "portfolio_id": {"type": "integer"}
            },
            "required": ["portfolio_id"]
        }
    )
    async def portfolio_news_cb(portfolio_id: int):
        from app.news.impact import PortfolioImpactEngine
        from app.core.database import AsyncSessionLocal
        from app.models.news import NewsArticle, NewsEntity, NewsEvent, NewsSentiment
        from sqlalchemy.future import select
        try:
            async with AsyncSessionLocal() as db:
                engine = PortfolioImpactEngine(db)
                from app.models.portfolio import Portfolio
                p_res = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
                portfolio = p_res.scalar_one_or_none()
                if not portfolio: return {"error": "Not found"}
                
                res = await db.execute(select(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(5))
                articles = res.scalars().all()
                all_impacts = []
                for a in articles:
                    ent_res = await db.execute(select(NewsEntity).where(NewsEntity.article_id == a.id))
                    ev_res = await db.execute(select(NewsEvent).where(NewsEvent.article_id == a.id))
                    sen_res = await db.execute(select(NewsSentiment).where(NewsSentiment.article_id == a.id))
                    from app.schemas.news import NewsEntitySchema, NewsEventSchema
                    e_schemas = [NewsEntitySchema(entity_type=e.entity_type, entity_name=e.entity_name) for e in ent_res.scalars().all()]
                    ev_schemas = [NewsEventSchema(event_type=e.event_type, details=e.details) for e in ev_res.scalars().all()]
                    s = sen_res.scalar_one_or_none()
                    impacts = await engine.determine_impact(portfolio.user_id, e_schemas, ev_schemas, s.score if s else 0.0)
                    all_impacts.extend([i.model_dump() for i in impacts if i.portfolio_id == portfolio_id])
                return all_impacts
        except Exception as e:
            return {"error": str(e)}
    registry.register(portfolio_news_tool, portfolio_news_cb)

    logger.info("Registered Agent tools successfully.")
