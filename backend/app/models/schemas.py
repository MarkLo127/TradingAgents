"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    deep_think_llm: Optional[str] = Field(default="gpt-4o-mini", description="Deep thinking LLM model")
    quick_think_llm: Optional[str] = Field(default="gpt-4o-mini", description="Quick thinking LLM model")
    
    # API Configuration
    openai_api_key: str = Field(..., description="OpenAI API Key (required)", min_length=10)
    openai_base_url: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API Base URL (optional)"
    )
    alpha_vantage_api_key: Optional[str] = Field(
        None,
        description="Alpha Vantage API Key (optional, for enhanced data)"
    )


class AnalysisResponse(BaseModel):
    """Response model for trading analysis"""
    status: str = Field(..., description="Analysis status (success, error, processing)")
    ticker: str = Field(..., description="Stock ticker analyzed")
    analysis_date: str = Field(..., description="Date of analysis")
    decision: Optional[Dict[str, Any]] = Field(None, description="Trading decision details")
    reports: Optional[Dict[str, Any]] = Field(None, description="Analysis reports from different teams")
    error: Optional[str] = Field(None, description="Error message if analysis failed")


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
