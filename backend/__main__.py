"""
Backend module entry point
Run with: python -m backend
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add parent directory to path to import tradingagents
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


def main():
    """Start the FastAPI server"""
    # Get host and port from environment variables with defaults
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    reload = os.getenv("BACKEND_RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting TradingAgents Backend Server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"\n📖 API Documentation: http://{host}:{port}/docs")
    print(f"📊 Health Check: http://{host}:{port}/api/health\n")
    
    # Start uvicorn server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
