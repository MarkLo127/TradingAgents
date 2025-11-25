# -*- coding: utf-8 -*-
import time
import json


def create_risk_manager(llm, memory):
    """
    建立一個風險管理員（裁判）節點。

    這個節點扮演風險管理裁判和辯論主持人的角色。
    其目標是評估激進、中立和保守三位風險分析師之間的辯論，
    並根據辯論內容、分析報告以及過去的經驗，對交易員的計畫做出最終的、
    經過風險調整的決策（買入、賣出或持有）。

    Args:
        llm: 用於生成決策的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表風險管理員節點的函式，可在 langgraph 中使用。
    """

    def risk_manager_node(state) -> dict:
        """
        風險管理員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含最終的交易決策。
        """
        # 從狀態中獲取所需資訊
        company_name = state["company_of_interest"]
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state["history"]
        
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"] # 這裡原文似乎有誤，應為 fundamentals_report
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

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
        trader_plan = truncate_text(trader_plan, 800)
        
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
        # 限制辯論歷史在 1000 字符以內（風險辯論通常有3方，比投資辯論更長）
        history = truncate_text(history, 1000)

        
        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是風險管理經理，負責評估投資計畫的風險並做出最終風控決策。**您必須保持嚴格中立觀點，綜合評估積極、中立、保守三方風險觀點，基於風險調整做出最終決策。**

【職責】
1. **評估辯論**：綜合積極、中立、保守三方的風險觀點，不偏袒任何一方
2. **識別風險**：系統性評估市場、財務、營運等多維度風險
3. **最終決策**：基於風險調整後的買入/賣出/持有決策，展現獨立判斷
4. **風控設定**：建立明確的風險管理框架與具體參數
5. **中立裁判**：**作為風險中立裁判，綜合三方觀點後做出獨立決策**

【可用資訊】
- 過去反思："{past_memory_str}"
- 交易員計畫：{trader_plan}
- 辯論歷史：{history}

【輸出要求】
**字數要求**：**至少800字以上**
**內容結構**：
1. 風控結論（150字以上）：風險評級與最終決策的明確陳述
2. 論證評估（200字以上）：三方風險觀點的綜合評估，公正分析
3. 風險分析（300字以上）：主要風險因素與量化評估，多維度分析
4. 最終決策（100字以上）：經風險調整的操作建議與部位規模
5. 風控措施（50字以上）：停損、監控指標、應急預案等具體措施

**撰寫原則**：
- **嚴格中立**：綜合評估積極、保守、中立三方觀點，不偏袒任何一方
- **獨立決策**：基於風險評估做出獨立判斷，展現決策自主性
- 決策明確，風控參數具體，確保可執行性
- 保守謹慎，但避免過度保守影響報酬
- 提供完整的風險管理框架與具體措施

**結尾提示**：
請在報告最後加上以下結尾：
「---
🎯 **本報告為風險管理經理的最終決策，綜合三方風險觀點（積極、保守、平衡）後做出。風控框架需嚴格執行。投資有風險，請謹慎評估。**」

請提供專業且全面的風險管理決策報告。"""
        

        # 呼叫 LLM 生成決策
        response = llm.invoke(prompt)

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        # 返回更新後的狀態，包括最終交易決策
        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node