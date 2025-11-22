"""
API route definitions for TradingAgents Backend
"""
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import logging
import threading

from backend.app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ConfigResponse,
    HealthResponse,
    Ticker,
    TaskCreatedResponse,
    TaskStatusResponse,
)
from backend.app.services.trading_service import TradingService
from backend.app.services.task_manager import task_manager
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


@router.post("/analyze", response_model=TaskCreatedResponse)
async def run_analysis(
    request: AnalysisRequest,
    service: TradingService = Depends(get_trading_service),
):
    """
    Start an async trading analysis task.
    
    This endpoint creates an async task and returns immediately with a task ID.
    Use the /api/task/{task_id} endpoint to check the status and get results.
    
    Args:
        request: Analysis request configuration
        service: Trading service instance (injected)
    
    Returns:
        TaskCreatedResponse: Task ID and initial status
    """
    logger.info(f"Creating analysis task for {request.ticker} on {request.analysis_date}")
    
    # Create task in Redis
    task_id = task_manager.create_task({
        "ticker": request.ticker,
        "analysis_date": request.analysis_date,
    })
    
    # Start background analysis
    def run_background_analysis():
        import asyncio
        
        try:
            task_manager.update_task_status(
                task_id,
                "running",
                progress="Starting analysis..."
            )
            
            # Run async function in sync context
            result = asyncio.run(service.run_analysis(
                ticker=request.ticker,
                analysis_date=request.analysis_date,
                analysts=request.analysts,
                research_depth=request.research_depth,
                deep_think_llm=request.deep_think_llm,
                quick_think_llm=request.quick_think_llm,
                openai_api_key=request.openai_api_key or "",  # Pass empty string if None, service handles it
                openai_base_url=request.openai_base_url,
                quick_think_base_url=request.quick_think_base_url,
                deep_think_base_url=request.deep_think_base_url,
                quick_think_api_key=request.quick_think_api_key or "",
                deep_think_api_key=request.deep_think_api_key or "",
                embedding_base_url=request.embedding_base_url,
                embedding_api_key=request.embedding_api_key or "",
                alpha_vantage_api_key=request.alpha_vantage_api_key,
            ))
            
            # Check for errors in result
            if "status" in result and result["status"] == "error":
                task_manager.set_task_error(
                    task_id,
                    error=result.get("message", "Analysis failed")
                )
            else:
                task_manager.set_task_result(task_id, result=result)
                
        except Exception as e:
            logger.error(f"Analysis task {task_id} failed: {str(e)}", exc_info=True)
            task_manager.set_task_error(
                task_id,
                error=str(e)
            )
    
    # Start background thread
    thread = threading.Thread(target=run_background_analysis, daemon=True)
    thread.start()
    
    return TaskCreatedResponse(
        task_id=task_id,
        status="pending",
        message="Analysis task created successfully"
    )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of an analysis task.
    
    Args:
        task_id: Task identifier
    
    Returns:
        TaskStatusResponse: Current task status and results if completed
    
    Raises:
        HTTPException: If task not found
    """
    task = task_manager.get_task_status(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskStatusResponse(**task)


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
