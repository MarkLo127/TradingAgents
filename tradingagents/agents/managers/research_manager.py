# -*- coding: utf-8 -*-
import time
import json


def create_research_manager(llm, memory):
    """
    建立一個研究管理員（裁判）節點。

    這個節點扮演投資組合經理和辯論主持人的角色。
    其任務是評估看漲和看跌分析師之間的辯論，並做出最終的投資決策
    （與看跌方一致、與看漲方一致，或在有充分理由時選擇持有）。
    它還需要制定一個詳細的投資計畫給交易員。

    Args:
        llm: 用於生成決策和計畫的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表研究管理員節點的函式，可在 langgraph 中使用。
    """

    def research_manager_node(state) -> dict:
        """
        研究管理員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含裁判的決策和投資計畫。
        """
        # 從狀態中獲取所需資訊
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 定義文本截斷函數以避免超過 token 限制
        def truncate_text(text, max_chars):
            """截斷文本到指定字符數"""
            if len(text) <= max_chars:
                return text
            return text[:max_chars] + "\n...(內容已截斷)"
        
        # 為每個報告設置合理的字符限制
        # 模型 gpt-5-mini 的限制是 8192 tokens
        # 混合中英文估算: 1 字符 ≈ 1.5-2 tokens (取保守值)
        # 目標: 總字符數 < 3500 字符 (約 5250-7000 tokens，留足夠 tokens 給 completion)
        market_research_report = truncate_text(market_research_report, 500)
        sentiment_report = truncate_text(sentiment_report, 500)
        news_report = truncate_text(news_report, 600)
        fundamentals_report = truncate_text(fundamentals_report, 600)
        
        # 整合當前情況
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
        
        # 截斷辯論歷史 - 這是最容易超過限制的部分
        # 限制辯論歷史在 1200 字符以內
        history = truncate_text(history, 1200)

        # 建立提示 (prompt)
        prompt = f"""作為投資組合經理和辯論主持人，您的角色是批判性地評估這一輪辯論，並做出明確的決定：與看跌分析師保持一致、與看漲分析師保持一致，或者僅在有充分理由支持的情況下選擇持有。

簡潔地總結雙方的要點，重點關注最有說服力的證據或推理。您的建議——買入、賣出或持有——必須清晰且可操作。避免僅僅因為雙方都有道理就預設為持有；請根據辯論中有力的論點堅定立場。

此外，為交易員制定一個詳細的投資計畫。這應包括：

您的建議：一個由具說服力的論點支持的果斷立場。
理由：解釋為何這些論點導向您的結論。
策略性行動：實施建議的具體步驟。
考慮您在類似情況下的過去錯誤。利用這些見解來完善您的決策過程，並確保您在學習和進步。請以對話方式呈現您的分析，就像自然說話一樣，不帶任何特殊格式。

以下是您對過去錯誤的反思：
\"{past_memory_str}\" 

這是本次辯論：
辯論歷史：
{history}"""
        
        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 更新投資辯論狀態
        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        # 返回更新後的狀態，包括裁判的決策和投資計畫
        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node