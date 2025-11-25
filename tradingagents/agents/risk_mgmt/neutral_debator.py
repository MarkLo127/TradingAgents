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
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是平衡型策略師，客觀評估風險與報酬的性價比。

【論證重點】
1. **客觀權衡**：不偏多也不偏空，只看數據。
2. **情境分析**：什麼情況下該買？什麼情況下該賣？
3. **策略優化**：有沒有比單純買進或賣出更好的做法？（如分批、對沖）
4. **調解分歧**：整合激進與保守的觀點。

【可用資訊】
- 交易員計畫：{trader_decision}
- 各類報告：{market_research_report}, {sentiment_report}, {news_report}, {fundamentals_report}
- 辯論歷史：{history}
- 對手觀點：{current_risky_response}, {current_safe_response}

【輸出要求】
**長度**：200-350字（中立客觀）
**結構**：
1. 核心觀點（50字）：持平而論。
2. 損益分析（100-150字）：分析勝率與賠率。
3. 評論對手（50-100字）：指出雙方都沒看到的盲點。
4. 操作建議（50字）：穩健的折衷方案。

**注意**：
- 尋求最佳平衡點。
- 不要當牆頭草，要有自己的判斷。
- 提供務實的建議。

請提供一份平衡且客觀的投資論證！"""

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