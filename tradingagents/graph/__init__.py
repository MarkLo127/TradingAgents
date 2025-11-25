# -*- coding: utf-8 -*-
# TradingAgentsX/graph/__init__.py

"""
這個 `__init__.py` 檔案將 `graph` 目錄標記為一個 Python 套件。

它匯入了此套件中的主要類別，以便使用者可以更方便地從 `tradingagents.graph` 直接匯入它們，
而不需要知道每個類別所在的具體模組檔案。

匯出的類別包括：
- TradingAgentsXGraph: 整個交易代理圖的主要協調器。
- ConditionalLogic: 處理圖中條件分支邏輯的類別。
- GraphSetup: 負責設定和建立圖結構的類別。
- Propagator: 管理狀態在圖中節點之間傳播的類別。
- Reflector: 處理對決策的反思和記憶更新的類別。
- SignalProcessor: 處理最終信號並做出交易決策的類別。
"""

# 從同層級的模組中匯入類別
from .trading_graph import TradingAgentsXGraph
from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor

# `__all__` 變數定義了當 `from tradingagents.graph import *` 被執行時，
# 哪些名稱會被匯入。這是一種控制命名空間的良好實踐。
__all__ = [
    "TradingAgentsXGraph",
    "ConditionalLogic",
    "GraphSetup",
    "Propagator",
    "Reflector",
    "SignalProcessor",
]