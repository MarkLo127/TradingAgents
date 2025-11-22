"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import date


class AnalysisRequest(BaseModel):
    """Request model for trading analysis"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'NVDA', 'AAPL')", min_length=1, max_length=10)
    analysis_date: str = Field(..., description="Analysis date in YYYY-MM-DD format")
    analysts: Optional[List[str]] = Field(
        default=["market", "social", "news", "fundamentals"],
        description="List of analysts to include in analysis"
    )
    research_depth: Optional[int] = Field(default=1, ge=1, le=5, description="Research depth (1-5)")
    deep_think_llm: Optional[str] = Field(default="gpt-5-mini-2025-08-07", description="Deep thinking LLM model")
    quick_think_llm: Optional[str] = Field(default="gpt-5-mini-2025-08-07", description="Quick thinking LLM model")
    
    # API Configuration
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key (optional if set on server)", min_length=0)
    openai_base_url: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API Base URL (optional)"
    )
    alpha_vantage_api_key: Optional[str] = Field(
        None,
        description="Alpha Vantage API Key (optional, for enhanced data)"
    )


class PriceData(BaseModel):
    """Stock price data model"""
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: int


class PriceStats(BaseModel):
    """Price statistics model"""
    growth_rate: float = Field(..., description="Price growth rate in percentage")
    duration_days: int = Field(..., description="Data duration in days")
    start_date: str
    end_date: str
    start_price: float
    end_price: float


class AnalysisResponse(BaseModel):
    """Response model for trading analysis"""
    status: str = Field(..., description="Analysis status (success, error, processing)")
    ticker: str = Field(..., description="Stock ticker analyzed")
    analysis_date: str = Field(..., description="Date of analysis")
    decision: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Trading decision (string or details dict)")
    reports: Optional[Dict[str, Any]] = Field(None, description="Analysis reports from different teams")
    error: Optional[str] = Field(None, description="Error message if analysis failed")
    price_data: Optional[List[PriceData]] = Field(None, description="Historical price data")
    price_stats: Optional[PriceStats] = Field(None, description="Price statistics")


class ConfigResponse(BaseModel):
    """Response model for configuration options"""
    available_analysts: List[str] = Field(..., description="Available analyst types")
    available_llms: List[str] = Field(..., description="Available LLM models")
    default_config: Dict[str, Any] = Field(..., description="Default configuration values")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server timestamp")


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")


class Ticker(BaseModel):
    """Ticker information model"""
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")


# Task Management Schemas

class TaskCreatedResponse(BaseModel):
    """Response when a task is created"""
    task_id: str = Field(..., description="Unique task identifier")
    status: Literal["pending"] = Field(default="pending", description="Initial task status")
    message: str = Field(default="Analysis task created successfully", description="Success message")


class TaskStatusResponse(BaseModel):
    """Response for task status query"""
    task_id: str = Field(..., description="Task identifier")
    status: Literal["pending", "running", "completed", "failed"] = Field(..., description="Current task status")
    created_at: str = Field(..., description="Task creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    progress: Optional[str] = Field(None, description="Progress message")
    result: Optional[AnalysisResponse] = Field(None, description="Analysis result (only when completed)")
    error: Optional[str] = Field(None, description="Error message (only when failed)")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
