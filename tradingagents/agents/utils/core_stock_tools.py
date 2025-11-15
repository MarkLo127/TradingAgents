from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_stock_data(
    symbol: Annotated[str, "公司的股票代碼"],
    start_date: Annotated[str, "開始日期，格式為 yyyy-mm-dd"],
    end_date: Annotated[str, "結束日期，格式為 yyyy-mm-dd"],
) -> str:
    """
    檢索給定股票代碼的股價數據 (OHLCV)。
    使用設定的核心股票 API 供應商。
    Args:
        symbol (str): 公司的股票代碼，例如 AAPL, TSM
        start_date (str): 開始日期，格式為 yyyy-mm-dd
        end_date (str): 結束日期，格式為 yyyy-mm-dd
    Returns:
        str: 一個格式化的數據框，包含指定股票代碼在指定日期範圍內的股價數據。
    """
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)