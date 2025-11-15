# -*- coding: utf-8 -*-
import time
import json


def create_risky_debator(llm):
    """
    建立一個激進的風險辯論員節點。

    這個節點在風險評估辯論中扮演激進派的角色。
    其目標是積極倡導高回報、高風險的機會，強調大膽的策略和競爭優勢。
    它會專注於潛在的上升空間，並挑戰保守和中立的觀點。

    Args:
        llm: 用於生成回應的語言模型。

    Returns:
        function: 一個代表激進辯論員節點的函式，可在 langgraph 中使用。
    """

    def risky_node(state) -> dict:
        """
        激進辯論員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的風險辯論狀態。
        """
        # 從狀態中獲取風險辯論的相關資訊
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        # 獲取其他辯論者的最新回應
        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 從狀態中獲取各類分析報告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 獲取交易員的決策
        trader_decision = state["trader_investment_plan"]

        # 建立提示 (prompt)
        prompt = f"""作為激進風險分析師，您的角色是積極倡導高回報、高風險的機會，強調大膽的策略和競爭優勢。在評估交易員的決策或計畫時，請專注於潛在的上升空間、增長潛力和創新效益——即使這些都伴隨著較高的風險。利用所提供的市場數據和情緒分析來加強您的論點，並挑戰反對意見。具體來說，請直接回應保守和中立分析師提出的每點，用數據驅動的反駁和有說服力的推理進行反擊。強調他們的謹慎可能錯失關鍵機會，或者他們的假設可能過於保守。這是交易員的決策：

{trader_decision}

您的任務是通過質疑和批評保守及中立的立場，為交易員的決策建立一個令人信服的案例，以證明您的高回報視角為何能提供最佳的前進道路。將以下來源的見解融入您的論點中：

市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務報告：{news_report}
公司基本面報告：{fundamentals_report}
這是當前的對話歷史：{history} 這是保守分析師的最新論點：{current_safe_response} 這是中立分析師的最新論點：{current_neutral_response}。如果其他觀點沒有回應，請不要憑空捏造，只需陳述您的觀點。

積極參與，解決提出的任何具體問題，反駁他們邏輯上的弱點，並主張冒險的好處以超越市場常規。保持專注於辯論和說服，而不僅僅是呈現數據。挑戰每一個反駁觀點，以強調為何高風險方法是最佳選擇。請以對話方式輸出，就像您在說話一樣，不帶任何特殊格式。"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"激進分析師：{response.content}"

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",  # 記錄最新的發言者
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node