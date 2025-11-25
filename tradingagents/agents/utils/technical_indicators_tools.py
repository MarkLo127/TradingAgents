from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor

@tool
def get_indicators(
    symbol: Annotated[str, "公司的股票代碼"],
    indicator: Annotated[str, "要獲取分析和報告的技術指標"],
    curr_date: Annotated[str, "您正在交易的當前交易日期，格式為 YYYY-mm-dd"],
    look_back_days: Annotated[int, "回溯天數"] = 30,
) -> str:
    """
    檢索給定股票代碼的技術指標。
    使用設定的技術指標供應商。
    Args:
        symbol (str): 公司的股票代碼，例如 AAPL, TSM
        indicator (str): 要獲取分析和報告的技術指標
        curr_date (str): 您正在交易的當前交易日期，格式為 YYYY-mm-dd
        look_back_days (int): 回溯天數，預設為 30
    Returns:
        str: 一個格式化的數據框，包含指定股票代碼和指標的技術指標。
    """
    # 規範化指標名稱以匹配供應商的預期格式
    indicator_lower = indicator.lower().strip()
    
    # 處理常見的變體
    if "50" in indicator_lower and ("ma" in indicator_lower or "avg" in indicator_lower):
        normalized_indicator = "close_50_sma"
    elif "200" in indicator_lower and ("ma" in indicator_lower or "avg" in indicator_lower):
        normalized_indicator = "close_200_sma"
    elif "10" in indicator_lower and "ema" in indicator_lower:
        normalized_indicator = "close_10_ema"
    else:
        # 常見指標名稱映射
        mapping = {
            "sma50": "close_50_sma",
            "sma200": "close_200_sma",
            "ema10": "close_10_ema",
            "bbands": "boll",
            "bollinger": "boll",
            "bollinger bands": "boll",
            "macd_signal": "macds",
            "macd_hist": "macdh",
            "50-day ma": "close_50_sma",
            "200-day ma": "close_200_sma",
            "50 day ma": "close_50_sma",
            "200 day ma": "close_200_sma",
        }
        
        # 如果在映射中，使用映射名稱
        if indicator_lower in mapping:
            normalized_indicator = mapping[indicator_lower]
        # 如果已經是正確的格式（例如 rsi, macd, atr），則保持原樣（轉小寫）
        else:
            normalized_indicator = indicator_lower
        
    return route_to_vendor("get_indicators", symbol, normalized_indicator, curr_date, look_back_days)
