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
                logger.info(f"嘗試主動獲取 {ticker} 的價格數據...")
                
                # 主動獲取數據
                df = PriceService._fetch_and_cache_data(ticker, data_cache_dir)
                if df is not None:
                    return df
                else:
                    return None
            
            # Use the most recent file and check if it's still valid (< 24 hours)
            latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
            
            if not PriceService._is_cache_valid(latest_file):
                logger.info(f"{ticker} 緩存過期，重新獲取數據...")
                df = PriceService._fetch_and_cache_data(ticker, data_cache_dir)
                if df is not None:
                    return df
                # 如果獲取失敗，使用舊緩存
                logger.warning(f"使用過期緩存作為備援")
            
            logger.info(f"Loading price data from {latest_file}")
            
            df = pd.read_csv(latest_file)
            df['Date'] = pd.to_datetime(df['Date'])
            
            return df.sort_values('Date')
            
        except Exception as e:
            logger.error(f"Error loading price data for {ticker}: {e}")
            return None
    
    @staticmethod
    def _is_cache_valid(file_path: Path, max_age_hours: int = 24) -> bool:
        """
        Check if cache file is still valid based on modification time
        
        Args:
            file_path: Path to the cache file
            max_age_hours: Maximum age in hours before cache is considered stale
            
        Returns:
            True if cache is valid, False otherwise
        """
        import time
        file_mtime = file_path.stat().st_mtime
        current_time = time.time()
        cache_age_hours = (current_time - file_mtime) / 3600
        return cache_age_hours < max_age_hours
    
    @staticmethod
    def _fetch_and_cache_data(ticker: str, data_cache_dir: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
        """
        Fetch data from yfinance and cache it
        
        Args:
            ticker: Stock ticker symbol
            data_cache_dir: Path to data cache directory
            max_retries: Maximum number of retry attempts
            
        Returns:
            DataFrame with price data or None if failed
        """
        import yfinance as yf
        from datetime import datetime, timedelta
        import time as time_module
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 15)  # 15 years of data
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"嘗試從 Yahoo Finance 獲取 {ticker} 數據（第 {attempt} 次嘗試）...")
                
                # Download data with timeout
                data = yf.download(
                    ticker,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    progress=False,
                    timeout=30
                )
                
                if data.empty:
                    logger.error(f"{ticker} 無可用數據")
                    return None
                
                # Reset index to make Date a column
                data = data.reset_index()
                
                # Ensure cache directory exists
                Path(data_cache_dir).mkdir(parents=True, exist_ok=True)
                
                # Save to cache
                cache_file = Path(data_cache_dir) / f"{ticker}-YFin-data-{start_date.strftime('%Y-%m-%d')}-{end_date.strftime('%Y-%m-%d')}.csv"
                data.to_csv(cache_file, index=False)
                
                logger.info(f"成功獲取並緩存 {ticker} 數據到 {cache_file}")
                
                # Prepare and return DataFrame
                df = pd.read_csv(cache_file)
                df['Date'] = pd.to_datetime(df['Date'])
                return df.sort_values('Date')
                
            except Exception as e:
                logger.warning(f"第 {attempt} 次嘗試失敗: {e}")
                if attempt < max_retries:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff
                    logger.info(f"將在 {wait_time} 秒後重試...")
                    time_module.sleep(wait_time)
                else:
                    logger.error(f"在 {max_retries} 次嘗試後仍無法獲取 {ticker} 數據")
                    return None
        
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
