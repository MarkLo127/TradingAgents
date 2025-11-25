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
您是風險委員會主席，負責最終風險評估與決策。

【職責】
1. **評估辯論**：衡量激進/中立/保守觀點
2. **識別風險**：市場、財務、營運風險
3. **最終決策**：買入/賣出/持有（經風險調整）
4. **風控框架**：設定限額與止損

【可用資訊】
- 過去反思："{past_memory_str}"
- 交易員計畫：{trader_plan}
- 辯論歷史：{history}

【輸出要求】
**長度**：400-600字
**結構**：
1. 執行摘要（50字）：風險評級與決策
2. 辯論評估（100字）：三方觀點總結
3. 風險分析（150字）：主要風險因素
4. 最終決策（100字）：買/賣/持與部位建議
5. 風控措施（100字）：止損、對沖、監控

**注意**：
- 決策必須明確
- 包含具體風控指標
- 保守謹慎原則

請提供全面且可執行的風險管理方案！"""
        

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