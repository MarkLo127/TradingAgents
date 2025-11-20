"""
Price data service for loading and processing stock price data
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PriceService:
    """Service for loading and processing price data from data_cache"""
    
    @staticmethod
    def load_price_data(ticker: str, data_cache_dir: str) -> Optional[pd.DataFrame]:
        """
        Load price data from data_cache CSV files
        
        Args:
            ticker: Stock ticker symbol
            data_cache_dir: Path to data cache directory
            
        Returns:
            DataFrame with price data or None if not found
        """
        try:
            cache_path = Path(data_cache_dir)
            
            # Search for {ticker}-YFin-data-*.csv files
            csv_files = list(cache_path.glob(f"{ticker}-YFin-data-*.csv"))
            
            if not csv_files:
                logger.warning(f"No price data found for {ticker} in {data_cache_dir}")
                return None
            
            # Use the most recent file
            latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Loading price data from {latest_file}")
            
            df = pd.read_csv(latest_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            return df.sort_values('Date')
            
        except Exception as e:
            logger.error(f"Error loading price data for {ticker}: {e}")
            return None
    
    @staticmethod
    def calculate_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate price statistics
        
        Args:
            df: DataFrame with price data
            
        Returns:
            Dictionary with statistics
        """
        start_price = float(df.iloc[0]['Close'])
        end_price = float(df.iloc[-1]['Close'])
        growth_rate = ((end_price - start_price) / start_price) * 100
        duration_days = (df.iloc[-1]['Date'] - df.iloc[0]['Date']).days
        
        return {
            "growth_rate": round(growth_rate, 2),
            "duration_days": int(duration_days),
            "start_date": df.iloc[0]['Date'].strftime('%Y-%m-%d'),
            "end_date": df.iloc[-1]['Date'].strftime('%Y-%m-%d'),
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
        }
    
    @staticmethod
    def prepare_chart_data(df: pd.DataFrame, limit: int = 365) -> List[Dict[str, Any]]:
        """
        Prepare price data for charting (limit to recent data)
        
        Args:
            df: DataFrame with price data
            limit: Maximum number of data points to return
            
        Returns:
            List of dictionaries with price data
        """
        # Get recent data
        recent_df = df.tail(limit)
        
        # Convert to list of dicts
        data = []
        for _, row in recent_df.iterrows():
            data.append({
                "Date": row['Date'].strftime('%Y-%m-%d'),
                "Open": round(float(row['Open']), 2),
                "High": round(float(row['High']), 2),
                "Low": round(float(row['Low']), 2),
                "Close": round(float(row['Close']), 2),
                "Volume": int(row['Volume']),
            })
        
        return data
