from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.models.user import User
from app.analysis.engine import AnalysisEngine
from app.analysis.models import AnalysisReport
from app.market_data.service import MarketDataService

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.get("/{ticker}", response_model=AnalysisReport)
async def get_financial_analysis(
    ticker: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a full quantitative analysis, scoring, and valuation report.
    """
    try:
        md_service = MarketDataService()
        engine = AnalysisEngine(market_data_service=md_service)
        report = await engine.generate_full_report(ticker)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate analysis: {str(e)}")
