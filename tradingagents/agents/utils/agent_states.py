from typing import Annotated, Sequence
from datetime import date, timedelta, datetime
from typing_extensions import TypedDict, Optional
from langchain_openai import ChatOpenAI
from tradingagents.agents import *
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph, START, MessagesState


# 研究團隊狀態
class InvestDebateState(TypedDict):
    bull_history: Annotated[
        str, "看漲對話歷史"
    ]  # 看漲對話歷史
    bear_history: Annotated[
        str, "看跌對話歷史"
    ]  # 看跌對話歷史
    history: Annotated[str, "對話歷史"]  # 對話歷史
    current_response: Annotated[str, "最新回應"]  # 最新回應
    judge_decision: Annotated[str, "最終裁判決定"]  # 最終回應
    count: Annotated[int, "目前對話長度"]  # 對話長度


# 風險管理團隊狀態
class RiskDebateState(TypedDict):
    risky_history: Annotated[
        str, "激進代理人的對話歷史"
    ]  # 對話歷史
    safe_history: Annotated[
        str, "保守代理人的對話歷史"
    ]  # 對話歷史
    neutral_history: Annotated[
        str, "中立代理人的對話歷史"
    ]  # 對話歷史
    history: Annotated[str, "對話歷史"]  # 對話歷史
    latest_speaker: Annotated[str, "最後發言的分析師"]
    current_risky_response: Annotated[
        str, "激進分析師的最新回應"
    ]  # 最新回應
    current_safe_response: Annotated[
        str, "保守分析師的最新回應"
    ]  # 最新回應
    current_neutral_response: Annotated[
        str, "中立分析師的最新回應"
    ]  # 最新回應
    judge_decision: Annotated[str, "裁判的決定"]
    count: Annotated[int, "目前對話長度"]  # 對話長度


class AgentState(MessagesState):
    company_of_interest: Annotated[str, "我們感興趣的交易公司（股票代碼）"]
    company_name: Annotated[str, "公司的真實全名"]
    trade_date: Annotated[str, "我們的交易日期"]

    sender: Annotated[str, "發送此訊息的代理人"]

    # 研究步驟
    market_report: Annotated[str, "市場分析師的報告"]
    sentiment_report: Annotated[str, "社群媒體分析師的報告"]
    news_report: Annotated[
        str, "新聞研究員關於當前世界事務的報告"
    ]
    fundamentals_report: Annotated[str, "基本面研究員的報告"]

    # 研究團隊討論步驟
    investment_debate_state: Annotated[
        InvestDebateState, "關於是否投資的辯論的當前狀態"
    ]
    investment_plan: Annotated[str, "分析師產生的計畫"]

    trader_investment_plan: Annotated[str, "交易員產生的計畫"]

    # 風險管理團隊討論步驟
    risk_debate_state: Annotated[
        RiskDebateState, "關於評估風險的辯論的當前狀態"
    ]
    final_trade_decision: Annotated[str, "風險分析師做出的最終決定"]