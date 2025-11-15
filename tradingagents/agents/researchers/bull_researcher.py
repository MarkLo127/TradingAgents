# -*- coding: utf-8 -*-
from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    """
    建立一個看漲研究員節點。

    這個節點在辯論中扮演看漲分析師的角色，主張投資某支股票。
    它會利用市場研究、情緒分析、新聞和基本面報告，並結合過去的經驗（記憶），
    來構建一個有說服力的論點，並反駁看跌方的觀點。

    Args:
        llm: 用於生成回應的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表看漲研究員節點的函式，可在 langgraph 中使用。
    """

    def bull_node(state) -> dict:
        """
        看漲研究員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的投資辯論狀態。
        """
        # 從狀態中獲取投資辯論的相關資訊
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")
        current_response = investment_debate_state.get("current_response", "")

        # 從狀態中獲取各類分析報告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 整合當前情況
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        
        # 從記憶體中獲取過去相似情況的經驗
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 將過去的經驗格式化為字串
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 建立提示 (prompt)
        prompt = f"""您是一位主張投資該股票的看漲分析師。您的任務是建立一個強而有力、以證據為基礎的案例，強調其增長潛力、競爭優勢和積極的市場指標。利用所提供的研究和數據，有效解決疑慮並反駁看跌論點。

需要關注的要點：
- 增長潛力：突顯公司的市場機會、收入預測和可擴展性。
- 競爭優勢：強調獨特產品、強大品牌或主導市場地位等因素。
- 積極指標：使用財務健康狀況、行業趨勢和近期正面新聞作為證據。
- 看跌對應觀點：用具體數據和合理推理批判性地分析看跌論點，徹底解決疑慮，並說明為何看漲觀點更具說服力。
- 參與：以對話風格呈現您的論點，直接與看跌分析師的觀點互動，進行有效辯論，而不僅僅是羅列數據。

可用資源：
市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論的對話歷史：{history}
上次的看跌論點：{current_response}
從相似情況中得到的反思和經驗教訓：{past_memory_str}
利用這些資訊，提出一個令人信服的看漲論點，駁斥看跌方的擔憂，並進行一場動態辯論，展示看漲立場的優勢。您還必須處理反思，並從過去的錯誤和教訓中學習。
"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"看漲分析師：{response.content}"

        # 更新投資辯論狀態
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node