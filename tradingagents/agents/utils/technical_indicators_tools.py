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
    return route_to_vendor("get_indicators", symbol, indicator, curr_date, look_back_days)
