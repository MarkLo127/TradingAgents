"""
FastAPI application entry point for TradingAgents Backend
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

from backend.app.core.config import settings
from backend.app.core.cors import setup_cors
from backend.app.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-Agent LLM Financial Trading Framework - REST API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
setup_cors(app)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TradingAgents API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )
