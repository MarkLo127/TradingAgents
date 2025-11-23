# -*- coding: utf-8 -*-
from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    """
    建立一個看跌研究員節點。

    這個節點在辯論中扮演看跌分析師的角色，提出反對投資某支股票的論點。
    它會利用市場研究、情緒分析、新聞和基本面報告，並結合過去的經驗（記憶），
    來強調風險、挑戰和負面指標，並反駁看漲方的觀點。

    Args:
        llm: 用於生成回應的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表看跌研究員節點的函式，可在 langgraph 中使用。
    """

    def bear_node(state) -> dict:
        """
        看跌研究員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的投資辯論狀態。
        """
        # 從狀態中獲取投資辯論的相關資訊
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")
        current_response = investment_debate_state.get("current_response", "")

        # 從狀態中獲取各類分析報告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 整合當前情況並智能截斷以避免超過 token 限制
        # 估算：1 個中文字符 ≈ 2.5 tokens，1 個英文字符 ≈ 0.25 tokens
        # 目標：將每個報告限制在合理的字符數內，總共不超過約 15000 字符（約 20000-30000 tokens）
        
        def truncate_text(text, max_chars):
            """截斷文本到指定字符數"""
            if len(text) <= max_chars:
                return text
            return text[:max_chars] + "\n...(內容已截斷)"
        
        # 為每個報告設置合理的字符限制
        # 模型 gpt-4.1-mini 的限制是 8192 tokens
        # 混合中英文估算: 1 字符 ≈ 1.5-2 tokens (取保守值)
        # 目標: 總字符數 < 3000 字符 (約 4500-6000 tokens，留 2000+ tokens 給 completion)
        market_research_report = truncate_text(market_research_report, 500)
        sentiment_report = truncate_text(sentiment_report, 500)
        news_report = truncate_text(news_report, 800)  # 新聞通常較長但也需要控制
        fundamentals_report = truncate_text(fundamentals_report, 600)
        
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # 從記憶體中獲取過去相似情況的經驗
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 將過去的經驗格式化為字串（限制長度）
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            recommendation = rec["recommendation"]
            # 限制每條記憶的長度
            if len(recommendation) > 200:
                recommendation = recommendation[:200] + "...(已截斷)"
            past_memory_str += recommendation + "\n\n"

        # 建立提示 (prompt) - 限制歷史長度以控制總 token 數
        history = truncate_text(history, 300)
        current_response = truncate_text(current_response, 200)
        
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

您是一位提出反對投資該股票論點的看跌分析師。您的目標是提出一個理由充分的論點，強調風險、挑戰和負面指標。利用所提供的研究和數據，有效突顯潛在的缺點並反駁看漲論點。

需要關注的要點：

- 風險與挑戰：突顯可能阻礙股票表現的因素，如市場飽和、財務不穩定或宏觀經濟威脅。
- 競爭劣勢：強調脆弱性，如較弱的市場定位、創新能力下降或來自競爭對手的威脅。
- 負面指標：使用來自財務數據、市場趨勢或近期負面新聞的證據來支持您的立場。
- 看漲對應觀點：用具體數據和合理推理批判性地分析看漲論點，揭示其弱點或過於樂觀的假設。
- 參與：以對話風格呈現您的論點，直接與看漲分析師的觀點互動，進行有效辯論，而不僅僅是羅列事實。

可用資源：

市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論的對話歷史：{history}
上次的看漲論點：{current_response}
從相似情況中得到的反思和經驗教訓：{past_memory_str}
利用這些資訊，提出一個令人信服的看跌論點，駁斥看漲方的說法，並進行一場動態辯論，展示投資該股票的風險和弱點。您還必須處理反思，並從過去的錯誤和教訓中學習。
"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"看跌分析師：{response.content}"

        # 更新投資辯論狀態
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node