"""
API route definitions for TradingAgents Backend
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging

from backend.app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ConfigResponse,
    HealthResponse,
    Ticker,
)
from backend.app.services.trading_service import TradingService
from backend.app.api.dependencies import get_trading_service
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api", tags=["TradingAgents"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now().isoformat(),
    )


@router.get("/config", response_model=ConfigResponse)
async def get_config(service: TradingService = Depends(get_trading_service)):
    """Get available configuration options"""
    return ConfigResponse(
        available_analysts=service.get_available_analysts(),
        available_llms=service.get_available_llms(),
        default_config=service.get_default_config(),
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    service: TradingService = Depends(get_trading_service),
):
    """
    Run a comprehensive trading analysis for a given ticker and date.
    
    Requires OpenAI API key to be provided in the request.
    """
    logger.info(f"Received analysis request for {request.ticker} on {request.analysis_date}")
    
    # Run analysis with all provided parameters including API keys
    result = await service.run_analysis(
        ticker=request.ticker,
        analysis_date=request.analysis_date,
        openai_api_key=request.openai_api_key,
        openai_base_url=request.openai_base_url,
        alpha_vantage_api_key=request.alpha_vantage_api_key,
        analysts=request.analysts,
        research_depth=request.research_depth,
        deep_think_llm=request.deep_think_llm,
        quick_think_llm=request.quick_think_llm,
    )
    
    return result   


@router.get("/tickers")
async def get_tickers():
    """Get list of popular tickers (example endpoint)"""
    return {
        "tickers": [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
        ]
    }
