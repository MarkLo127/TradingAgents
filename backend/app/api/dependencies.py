"""
Shared dependencies for API routes
"""
from fastapi import Depends
from app.services.trading_service import TradingService, trading_service


def get_trading_service() -> TradingService:
    """Dependency to get trading service instance"""
    return trading_service
