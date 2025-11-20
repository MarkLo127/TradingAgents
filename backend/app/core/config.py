"""
Configuration management for TradingAgents Backend API
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    app_name: str = "TradingAgents API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Keys
    openai_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    
    # CORS Configuration
    cors_origins: list = [
        "http://localhost:3000",
        "http://frontend:3000",
    ]
    
    # TradingAgents Configuration
    results_dir: str = "./results"
    max_debate_rounds: int = 1
    max_risk_discuss_rounds: int = 1
    deep_think_llm: str = "gpt-4o-mini"
    quick_think_llm: str = "gpt-4o-mini"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
