# 獲取數據/統計資料

import yfinance as yf
from typing import Annotated, Callable, Any, Optional
from pandas import DataFrame
import pandas as pd
from functools import wraps

from .utils import save_output, SavePathType, decorate_all_methods


def init_ticker(func: Callable) -> Callable:
    """裝飾器，用於初始化 yf.Ticker 並將其傳遞給函式。"""

    @wraps(func)
    def wrapper(symbol: Annotated[str, "股票代碼"], *args, **kwargs) -> Any:
        ticker = yf.Ticker(symbol)
        return func(ticker, *args, **kwargs)

    return wrapper


@decorate_all_methods(init_ticker)
class YFinanceUtils:
    """
    一個提供 Yahoo Finance 數據獲取功能的工具類別。
    """

    def get_stock_data(
        symbol: Annotated[str, "股票代碼"],
        start_date: Annotated[
            str, "檢索股價數據的開始日期，格式為 YYYY-mm-dd"
        ],
        end_date: Annotated[
            str, "檢索股價數據的結束日期，格式為 YYYY-mm-dd"
        ],
        save_path: SavePathType = None,
    ) -> DataFrame:
        """檢索指定股票代碼的股價數據"""
        ticker = symbol
        # 將結束日期加一天，使數據範圍包含結束日期
        end_date = pd.to_datetime(end_date) + pd.DateOffset(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        stock_data = ticker.history(start=start_date, end=end_date)
        # save_output(stock_data, f"{ticker.ticker} 的股票數據", save_path)
        return stock_data

    def get_stock_info(
        symbol: Annotated[str, "股票代碼"],
    ) -> dict:
        """獲取並返回最新的股票資訊。"""
        ticker = symbol
        stock_info = ticker.info
        return stock_info

    def get_company_info(
        symbol: Annotated[str, "股票代碼"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """獲取並以 DataFrame 形式返回公司資訊。"""
        ticker = symbol
        info = ticker.info
        company_info = {
            "公司名稱": info.get("shortName", "N/A"),
            "行業": info.get("industry", "N/A"),
            "部門": info.get("sector", "N/A"),
            "國家": info.get("country", "N/A"),
            "網站": info.get("website", "N/A"),
        }
        company_info_df = DataFrame([company_info])
        if save_path:
            company_info_df.to_csv(save_path)
            print(f"{ticker.ticker} 的公司資訊已儲存至 {save_path}")
        return company_info_df

    def get_stock_dividends(
        symbol: Annotated[str, "股票代碼"],
        save_path: Optional[str] = None,
    ) -> DataFrame:
        """獲取並以 DataFrame 形式返回最新的股息數據。"""
        ticker = symbol
        dividends = ticker.dividends
        if save_path:
            dividends.to_csv(save_path)
            print(f"{ticker.ticker} 的股息已儲存至 {save_path}")
        return dividends

    def get_income_stmt(symbol: Annotated[str, "股票代碼"]) -> DataFrame:
        """獲取並以 DataFrame 形式返回公司最新的損益表。"""
        ticker = symbol
        income_stmt = ticker.financials
        return income_stmt

    def get_balance_sheet(symbol: Annotated[str, "股票代碼"]) -> DataFrame:
        """獲取並以 DataFrame 形式返回公司最新的資產負債表。"""
        ticker = symbol
        balance_sheet = ticker.balance_sheet
        return balance_sheet

    def get_cash_flow(symbol: Annotated[str, "股票代碼"]) -> DataFrame:
        """獲取並以 DataFrame 形式返回公司最新的現金流量表。"""
        ticker = symbol
        cash_flow = ticker.cashflow
        return cash_flow

    def get_analyst_recommendations(symbol: Annotated[str, "股票代碼"]) -> tuple:
        """獲取最新的分析師建議，並返回最常見的建議及其計數。"""
        ticker = symbol
        recommendations = ticker.recommendations
        if recommendations.empty:
            return None, 0  # 沒有可用的建議

        # 假設 'period' 欄位存在且需要排除
        row_0 = recommendations.iloc[0, 1:]  # 如有必要，排除 'period' 欄位

        # 尋找最大投票結果
        max_votes = row_0.max()
        majority_voting_result = row_0[row_0 == max_votes].index.tolist()

        return majority_voting_result[0], max_votes