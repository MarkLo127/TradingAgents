"""
TradingAgents service integration
"""
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add parent directory to path to import tradingagents
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class TradingService:
    """Service class for interacting with TradingAgents"""
    
    def __init__(self):
        self.default_config = DEFAULT_CONFIG.copy()
        
    def create_config(
        self,
        research_depth: int = 1,
        deep_think_llm: str = "gpt-4o-mini",
        quick_think_llm: str = "gpt-4o-mini",
    ) -> Dict[str, Any]:
        """Create configuration for TradingAgents"""
        config = self.default_config.copy()
        config["max_debate_rounds"] = research_depth
        config["max_risk_discuss_rounds"] = research_depth
        config["deep_think_llm"] = deep_think_llm
        config["quick_think_llm"] = quick_think_llm
        config["results_dir"] = settings.results_dir
        return config
    
    async def run_analysis(
        self,
        ticker: str,
        analysis_date: str,
        openai_api_key: str,
        openai_base_url: str = "https://api.openai.com/v1",
        alpha_vantage_api_key: Optional[str] = None,
        analysts: Optional[List[str]] = None,
        research_depth: int = 1,
        deep_think_llm: str = "gpt-4o-mini",
        quick_think_llm: str = "gpt-4o-mini",
    ) -> Dict[str, Any]:
        """
        Run trading analysis for a given ticker and date with user-provided API keys
        
        Args:
            ticker: Stock ticker symbol
            analysis_date: Date in YYYY-MM-DD format
            openai_api_key: OpenAI API Key (required)
            openai_base_url: OpenAI API Base URL (optional)
            alpha_vantage_api_key: Alpha Vantage API Key (optional)
            analysts: List of analyst types to include
            research_depth: Research depth (1-5)
            deep_think_llm: Deep thinking LLM model
            quick_think_llm: Quick thinking LLM model
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Default analysts if not provided
            if analysts is None:
                analysts = ["market", "sentiment", "news", "fundamentals"]
            
            # Dynamically set environment variables for this request
            import os
            original_openai_key = os.environ.get("OPENAI_API_KEY")
            original_alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
            
            try:
                # Set API keys for this request
                os.environ["OPENAI_API_KEY"] = openai_api_key
                if alpha_vantage_api_key:
                    os.environ["ALPHA_VANTAGE_API_KEY"] = alpha_vantage_api_key
                
                # Create configuration
                logger.info(f"Initializing TradingAgents for {ticker} on {analysis_date}")
                config = self.create_config(research_depth, deep_think_llm, quick_think_llm)
                
                # Override with user-provided settings
                config["llm_provider"] = "openai"
                config["backend_url"] = openai_base_url
                
                # Initialize TradingAgents graph
                graph = TradingAgentsGraph(analysts, config=config, debug=True)
                
                # Run analysis
                logger.info(f"Running analysis for {ticker}")
                final_state, decision = graph.propagate(ticker, analysis_date)
            
                # Extract reports from final state
                reports = {
                    "market_report": final_state.get("market_report"),
                    "sentiment_report": final_state.get("sentiment_report"),
                    "news_report": final_state.get("news_report"),
                    "fundamentals_report": final_state.get("fundamentals_report"),
                    "investment_plan": final_state.get("investment_plan"),
                    "trader_investment_plan": final_state.get("trader_investment_plan"),
                    "final_trade_decision": final_state.get("final_trade_decision"),
                    "investment_debate_state": final_state.get("investment_debate_state"),
                    "risk_debate_state": final_state.get("risk_debate_state"),
                }
                
                return {
                    "status": "success",
                    "ticker": ticker,
                    "analysis_date": analysis_date,
                    "decision": decision,
                    "reports": reports,
                }
                
            finally:
                # Clean up environment variables after request
                if original_openai_key is not None:
                    os.environ["OPENAI_API_KEY"] = original_openai_key
                elif "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
                    
                if original_alpha_key is not None:
                    os.environ["ALPHA_VANTAGE_API_KEY"] = original_alpha_key
                elif "ALPHA_VANTAGE_API_KEY" in os.environ:
                    del os.environ["ALPHA_VANTAGE_API_KEY"]
            
        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "ticker": ticker,
                "analysis_date": analysis_date,
                "error": str(e),
            }
    
    def get_available_analysts(self) -> List[str]:
        """Get list of available analyst types"""
        return ["market", "sentiment", "news", "fundamentals"]
    
    def get_available_llms(self) -> List[str]:
        """Get list of available OpenAI LLM models"""
        return [
            "gpt-5.1-2025-11-13",
            "gpt-5-mini-2025-08-07",
            "gpt-5-nano-2025-08-07",
            "gpt-4.1-mini",
            "gpt-4.1-nano",
            "gpt-4o",
            "gpt-4o-mini",
        ]
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "research_depth": 1,
            "deep_think_llm": "gpt-4o-mini",
            "quick_think_llm": "gpt-4o-mini",
            "max_debate_rounds": 1,
            "max_risk_discuss_rounds": 1,
        }


# Global service instance
trading_service = TradingService()
