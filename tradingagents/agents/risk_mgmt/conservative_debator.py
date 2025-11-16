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
        prompt = f"""作為安全/保守風險分析師，您的主要目標是保護資產、最小化波動性並確保穩定可靠的增長。您優先考慮穩定性、安全性和風險緩解，仔細評估潛在損失、經濟衰退和市場波動。在評估交易員的決策或計畫時，請批判性地審查高風險元素，指出決策可能使公司面臨過度風險的地方，以及更謹慎的替代方案可以在何處確保長期收益。這是交易員的決策：

{trader_decision}

您的任務是積極反駁激進和中立分析師的論點，強調他們的觀點可能忽略了潛在威脅或未能優先考慮可持續性。請直接回應他們的觀點，並從以下數據源中汲取資訊，為對交易員決策進行低風險方法調整建立一個有說服力的案例：

市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務報告：{news_report}
公司基本面報告：{fundamentals_report}
這是當前的對話歷史：{history} 這是激進分析師的最新回應：{current_risky_response} 這是中立分析師的最新回應：{current_neutral_response}。如果其他觀點沒有回應，請不要憑空捏造，只需陳述您的觀點。

通過質疑他們的樂觀情緒並強調他們可能忽略的潛在缺點來進行互動。處理他們的每一個反駁觀點，以展示為何保守立場最終是公司資產最安全的途徑。專注於辯論和批評他們的論點，以證明低風險策略優於他們的方法。請以對話方式輸出，就像您在說話一樣，不帶任何特殊格式。"""

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