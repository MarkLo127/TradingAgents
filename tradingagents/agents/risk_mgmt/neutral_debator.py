# -*- coding: utf-8 -*-
import time
import json


def create_neutral_debator(llm):
    """
    建立一個中立的風險辯論員節點。

    這個節點在風險評估辯論中扮演中立派的角色。
    其目標是提供一個平衡的視角，權衡交易員決策的潛在利益和風險。
    它會挑戰過於樂觀或過於謹慎的觀點，並倡導一個溫和、可持續的策略。

    Args:
        llm: 用於生成回應的語言模型。

    Returns:
        function: 一個代表中立辯論員節點的函式，可在 langgraph 中使用。
    """

    def neutral_node(state) -> dict:
        """
        中立辯論員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的風險辯論狀態。
        """
        # 從狀態中獲取風險辯論的相關資訊
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        # 獲取其他辯論者的最新回應
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

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
        current_safe_response = truncate_text(current_safe_response, 300)

        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

作為中立風險分析師，您的角色是提供一個平衡的視角，權衡交易員決策或計畫的潛在利益和風險。您優先考慮一個全面的方法，評估其優缺點，同時考慮更廣泛的市場趨勢、潛在的經濟轉變和多元化策略。這是交易員的決策：

{trader_decision}

您的任務是挑戰激進和安全分析師，指出每個觀點可能過於樂觀或過於謹慎的地方。利用以下數據源的見解，支持一個溫和、可持續的策略來調整交易員的決策：

市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務報告：{news_report}
公司基本面報告：{fundamentals_report}
這是當前的對話歷史：{history} 這是激進分析師的最新回應：{current_risky_response} 這是安全分析師的最新回應：{current_safe_response}。如果其他觀點沒有回應，請不要憑空捏造，只需陳述您的觀點。

通過批判性地分析雙方，積極參與，指出激進和保守論點中的弱點，以倡導一個更平衡的方法。挑戰他們的每一個觀點，以說明為何一個溫和的風險策略可能提供兩全其美的方案，既提供增長潛力，又防範極端波動。專注於辯論，而不僅僅是呈現數據，旨在表明一個平衡的觀點可以帶來最可靠的結果。請以對話方式輸出，就像您在說話一樣，不帶任何特殊格式。"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"中立分析師：{response.content}"

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",  # 記錄最新的發言者
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node