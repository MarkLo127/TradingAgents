# -*- coding: utf-8 -*-
# TradingAgents/graph/propagation.py

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


class Propagator:
    """
    處理狀態在圖中的初始化和傳播。
    這個類別負責建立圖執行的初始狀態，並提供圖呼叫所需的參數。
    """

    def __init__(self, max_recur_limit=100):
        """
        使用設定參數進行初始化。

        Args:
            max_recur_limit (int): 圖的最大遞迴深度限制，以防止無限循環。
        """
        self.max_recur_limit = max_recur_limit

    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """
        為代理圖建立初始狀態。
        這個狀態字典包含了執行開始時所需的所有資訊。

        Args:
            company_name (str): 感興趣的公司名稱或股票代碼。
            trade_date (str): 交易日期。

        Returns:
            Dict[str, Any]: 初始狀態的字典。
        """
        return {
            "messages": [("human", company_name)],  # 初始訊息，觸發第一個代理
            "company_of_interest": company_name,  # 感興趣的公司
            "trade_date": str(trade_date),  # 交易日期
            "investment_debate_state": InvestDebateState(
                {"history": "", "current_response": "", "count": 0}
            ),  # 投資辯論的初始狀態
            "risk_debate_state": RiskDebateState(
                {
                    "history": "",
                    "current_risky_response": "",
                    "current_safe_response": "",
                    "current_neutral_response": "",
                    "count": 0,
                }
            ),  # 風險辯論的初始狀態
            "market_report": "",  # 市場報告的初始值
            "fundamentals_report": "",  # 基本面報告的初始值
            "sentiment_report": "",  # 情緒報告的初始值
            "news_report": "",  # 新聞報告的初始值
        }

    def get_graph_args(self) -> Dict[str, Any]:
        """
        獲取圖呼叫的參數。
        這些參數控制著圖的執行方式，例如串流模式和遞迴限制。

        Returns:
            Dict[str, Any]: 用於圖呼叫的參數字典。
        """
        return {
            "stream_mode": "values",  # 設定串流模式為 "values"，以獲取每個節點的輸出
            "config": {"recursion_limit": self.max_recur_limit},  # 設定遞迴限制
        }