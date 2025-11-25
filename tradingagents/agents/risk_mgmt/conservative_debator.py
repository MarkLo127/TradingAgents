# -*- coding: utf-8 -*-
from langchain_core.messages import AIMessage
import time
import json


def create_safe_debator(llm):
    """
    建立一個安全/保守的風險辯論員節點。

    這個節點在風險評估辯論中扮演保守派的角色。
    其主要目標是保護資產、最小化波動性並確保穩定可靠的增長。
    它會優先考慮穩定性、安全性和風險緩解，並對交易員的決策提出謹慎的調整建議。

    Args:
        llm: 用於生成回應的語言模型。

    Returns:
        function: 一個代表保守辯論員節點的函式，可在 langgraph 中使用。
    """

    def safe_node(state) -> dict:
        """
        保守辯論員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的風險辯論狀態。
        """
        # 從狀態中獲取風險辯論的相關資訊
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        # 獲取其他辯論者的最新回應
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 從狀態中獲取各類分析報告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 獲取交易員的決策
        trader_decision = state["trader_investment_plan"]

        # 定義文本截斷函數以避免超過 token 限制
        def truncate_text(text, max_chars):
            """截斷文本到指定字符數"""
            if len(text) <= max_chars:
                return text
            return text[:max_chars] + "\n...(內容已截斷)"
        
        # 截斷各類輸入以控制 token 使用量
        # 模型限制: 8192 tokens，目標: < 3500 字符
        market_research_report = truncate_text(market_research_report, 500)
        sentiment_report = truncate_text(sentiment_report, 500)
        news_report = truncate_text(news_report, 600)
        fundamentals_report = truncate_text(fundamentals_report, 600)
        trader_decision = truncate_text(trader_decision, 800)
        history = truncate_text(history, 400)
        current_risky_response = truncate_text(current_risky_response, 300)
        current_neutral_response = truncate_text(current_neutral_response, 300)
        
        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是保守風險分析師，專注於資本保護與下檔風險。

【論證重點】
1. **下檔風險**：最壞情況的潛在損失
2. **被忽視風險**：市場未定價的威脅
3. **估值過高**：價格脫離基本面
4. **反駁激進**：指出激進觀點的盲點

【可用資訊】
- 交易員計畫：{trader_decision}
- 各類報告：{market_research_report}, {sentiment_report}, {news_report}, {fundamentals_report}
- 辯論歷史：{history}
- 對手觀點：{current_risky_response}, {current_neutral_response}

【輸出要求】
**長度**：300-500字
**結構**：
1. 核心保守論點（80字）
2. 風險與威脅分析（150字）
3. 反駁激進觀點（100字）
4. 投資建議（70字）

**注意**：
- 優先考慮本金安全
- 強調潛在風險
- 建議防禦性策略

請提供謹慎保守的投資論證！"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"安全分析師：{response.content}"

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",  # 記錄最新的發言者
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node