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
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是投資決策主筆，負責彙整多方觀點，拍板定案。

【職責】
1. **聽取辯論**：誰說得比較有道理？
2. **做出裁決**：現在到底是該買還是該賣？
3. **擬定戰略**：給交易員一個明確的方向。

【可用資訊】
- 過去反思："{past_memory_str}"
- 辯論歷史：{history}

【輸出要求】
**長度**：300-450字（決策明確）
**結構**：
1. 決策摘要（50字）：買入、賣出還是持有？
2. 觀點評析（100-150字）：為什麼採納某方的意見？
3. 核心理由（100字）：支持決策的關鍵證據。
4. 給交易員的指令（50-100字）：目標價、停損點、倉位控制。

**注意**：
- 不要模稜兩可。
- 必須給出具體數字。
- 決策要有邏輯支撐。

請提供一份明確且可執行的投資決策！"""
        
        
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