import pandas as pd
import yfinance as yf
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config, DATA_DIR


class StockstatsUtils:
    """
    一個提供股票統計功能的工具類別。
    """
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "公司的股票代碼"],
        indicator: Annotated[
            str, "基於公司股票數據的量化指標"
        ],
        curr_date: Annotated[
            str, "用於檢索股價數據的當前日期，格式為 YYYY-mm-dd"
        ],
    ):
        """
        獲取指定股票和指標的統計數據。

        Args:
            symbol (str): 公司的股票代碼。
            indicator (str): 要計算的量化指標。
            curr_date (str): 當前日期。

        Returns:
            float or str: 指標值或錯誤訊息。
        """
        # 獲取設定並設定數據目錄路徑
        config = get_config()
        online = config["data_vendors"]["technical_indicators"] != "local"

        df = None
        data = None

        if not online:
            try:
                data = pd.read_csv(
                    os.path.join(
                        DATA_DIR,
                        f"{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
                    )
                )
                df = wrap(data)
            except FileNotFoundError:
                raise Exception("Stockstats 失敗：尚未獲取 Yahoo Finance 數據！")
        else:
            # 獲取今天的日期 (YYYY-mm-dd) 以添加到快取
            today_date = pd.Timestamp.today()
            curr_date = pd.to_datetime(curr_date)

            end_date = today_date
            start_date = today_date - pd.DateOffset(years=15)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            # 獲取設定並確保快取目錄存在
            os.makedirs(config["data_cache_dir"], exist_ok=True)

            data_file = os.path.join(
                config["data_cache_dir"],
                f"{symbol}-YFin-data-{start_date}-{end_date}.csv",
            )

            if os.path.exists(data_file):
                data = pd.read_csv(data_file)
                data["Date"] = pd.to_datetime(data["Date"])
            else:
                data = yf.download(
                    symbol,
                    start=start_date,
                    end=end_date,
                    multi_level_index=False,
                    progress=False,
                    auto_adjust=True,
                )
                data = data.reset_index()
                data.to_csv(data_file, index=False)

            df = wrap(data)
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
            curr_date = curr_date.strftime("%Y-%m-%d")

        df[indicator]  # 觸發 stockstats 計算指標
        matching_rows = df[df["Date"].str.startswith(curr_date)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A：非交易日 (週末或假日)"