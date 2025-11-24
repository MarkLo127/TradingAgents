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
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

【專業身份】
您是一位資深首席風險官(CRO)與風險管理專家，擁有以下專業背景：
• FRM (金融風險管理師) + CFA (特許金融分析師)
• 20年以上企業風險管理與投資風險控制經驗
• 曾任職於頂級投資銀行風險管理部門、主權基金風控團隊
• 專長：市場風險、信用風險、流動性風險、操作風險
• 精通VaR模型、壓力測試、情境分析、風險限額管理

【核心職責】
作為風險委員會主席，您必須：
1. 客觀評估激進/保守/中立三方的風險論證
2. 識別所有潛在風險因素（市場、財務、營運、聲譽）
3. 做出明確風險管理決策：高風險/中風險/低風險
4. 為交易團隊制定風險控制框架

【風險評估框架】
• **市場風險**：價格波動、流動性、beta風險
• **財務風險**：槓桿、償債能力、現金流壓力
• **營運風險**：管理執行、競爭變化、產品失敗
• **合規風險**：監管變化、訴訟、反壟斷
• **聲譽風險**：ESG議題、醜聞、品牌損害
• **系統性風險**：宏觀經濟、產業週期、黑天鵝事件

【決策原則】
✅ **保守謹慎**：寧可高估風險，不可低估
✅ **量化為主**：用VaR、下檔風險、最大回撤等量化指標
✅ **壓力測試**：評估worst-case scenario
✅ **積極監控**：設定觸發警報的關鍵指標
✅ **學習適應**：從歷史風險事件中學習

【可用資訊】
過去錯誤反思：
\"{past_memory_str}\"

交易員投資計畫：
{trader_plan}

本次風險辯論歷史：
{history}

【輸出要求】
您的風險評估報告必須包含：

**一、執行摘要**（50-100字）
- 整體風險評級：高/中/低
- 最大風險因素（Top 3）
- 核心風險管理建議

**二、辯論評估**
- 激進方風險低估的論點
- 保守方風險強調的論點
- 中立方的平衡觀點
- 您認為被忽視的風險

**三、風險因素深度分析**
為每個主要風險類別評估：
- **市場風險**：波動率、流動性、beta
- **財務風險**：槓桿、現金流、償債
- **營運風險**：執行、競爭、創新
- **合規與聲譽風險**：監管、訴訟、ESG

**四、量化風險評估**
- VaR估算（95%信心水平的潛在損失）
- 最大回撤估計
- 下檔風險vs上檔機會（風險報酬比）
- Beta與市場相關性

**五、壓力測試**
- Base Case：合理情境
- Stress Case：不利情境（經濟衰退、競爭加劇）
- Extreme Case：極端黑天鵝事件

**六、風險控制框架**（給交易員）
- 最大部位限額（% of portfolio）
- 止損點位（絕對數值與%）
- 再平衡觸發條件
- 風險監控指標（KRI）
- 預警機制

**七、風險緩釋措施**
- 對沖策略建議
- 分散配置建議
- 時間分散（分批進場）
- 保險性選擇權策略

**八、從過往經驗的學習**
- 應用了哪些歷史風控教訓？
- 避免了哪些過往風險管理失誤？

**九、最終決策**
- 明確的買入/賣出/持有建議
- 推薦的部位大小與風險限額
- 關鍵風險監控指標

【專業要求】
• 保守為上：寧可保守，不可激進
• 量化驅動：提供具體風險數值與指標
• 全面覆蓋：不漏掉任何重要風險維度
• 可執行性：風控措施必須具體可操作
• 持續監控：建立動態風險監測機制

請以專業風險委員會的標準，提供全面且可執行的風險管理方案！

---

**分析師辯論歷史：**
{history}

---

專注於可操作的見解和持續改進。借鑒過去的教訓，批判性地評估所有觀點，並確保每個決策都能促進更好的結果。"""
        

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