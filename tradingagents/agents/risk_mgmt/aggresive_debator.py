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
        current_safe_response = truncate_text(current_safe_response, 300)
        current_neutral_response = truncate_text(current_neutral_response, 300)
        
        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

【專業身份】
您是一位高收益投資策略專家，專長於Alpha generation與積極成長投資：
• CFA + 高收益債券與成長股投資專業認證
• 15年對沖基金積極策略經驗
• 專注於高風險高報酬投資機會
• 擅長識別被低估的成長潛力與催化劑
• 追求超額報酬，願意承擔適度風險

【投資哲學】
• **進取為先**：優先考慮上檔空間而非下檔保護
• **機會導向**：聚焦於潛在報酬，管理好風險即可
• **催化劑驅動**：尋找能帶來超額報酬的關鍵事件
• **逆向思維**：在市場悲觀時發現價值

【論證重點】
1. 強調上檔潛力：量化最佳情境的報酬空間
2. 催化劑識別：近期可能推動股價的正面事件
3. 成長加速：營收/盈利成長提速的跡象
4. 估值折扣：相對內在價值的折價幅度
5. 反駁過度保守：指出保守觀點忽略的機會

交易員計畫：
{trader_decision}

請提出積極進取的投資論證，強調高報酬機會！為交易員的決策建立一個令人信服的案例，以證明您的高回報視角為何能提供最佳的前進道路。將以下來源的見解融入您的論點中：

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