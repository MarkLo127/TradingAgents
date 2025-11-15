# 匯入時間模組，用於計算執行時間
import time
# 從 tradingagents.dataflows.y_finance 模組匯入所需的函式
# 這些函式用於從 Yahoo Finance 獲取各種股票數據
from tradingagents.dataflows.y_finance import (
    get_YFin_data_online,  # 線上獲取 Yahoo Finance 數據
    get_stock_stats_indicators_window,  # 獲取特定時間窗口內的股票統計指標
    get_balance_sheet as get_yfinance_balance_sheet,  # 獲取資產負債表
    get_cashflow as get_yfinance_cashflow,  # 獲取現金流量表
    get_income_statement as get_yfinance_income_statement,  # 獲取損益表
    get_insider_transactions as get_yfinance_insider_transactions,  # 獲取內部交易資訊
)

# 測試案例說明
print("測試使用 30 天回溯期的優化實作：")

# 記錄開始時間
start_time = time.time()

# 呼叫函式，獲取蘋果公司（AAPL）在 2024-11-01 前 30 天的 MACD 指標
# 'macd' 是移動平均收斂發散指標，一種常用的技術分析工具
result = get_stock_stats_indicators_window("AAPL", "macd", "2024-11-01", 30)

# 記錄結束時間
end_time = time.time()

# 輸出函式執行的時間
print(f"執行時間：{end_time - start_time:.2f} 秒")
# 輸出結果的長度（字元數）
print(f"結果長度：{len(result)} 字元")
# 輸出獲取的指標結果
print(result)