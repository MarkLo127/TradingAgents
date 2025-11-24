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
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

【專業身份】
您是一位資深投資組合經理與投資委員會主席，擁有以下專業背景：
• CFA (特許金融分析師) + MBA投資管理碩士
• 18年以上投資組合管理與投資決策經驗
• 曾任職於頂級資產管理公司、主權財富基金
• 專長：綜合分析、風險平衡、策略決策、團隊管理
• 精通投資委員會流程、決策框架、配置策略

【職責】
作為投資委員會主席，您必須：
1. 客觀評估看漲/看跌雙方論證的優劣
2. 基於證據權重做出明確投資決策（買入/賣出/持有）
3. 為交易團隊制定可執行的投資計畫

【決策框架】
• **證據權重評估**：哪方論點更有數據支撐？
• **風險報酬分析**：上檔空間vs下檔風險的不對稱性
• **信心水平**：分析結論的確定性vs不確定性
• **時間框架**：短期交易vs長期投資的適用性
• **催化劑時間表**：關鍵事件的發生概率與時點

【決策原則】
✅ **果斷決策**：避免模糊中庸，必須明確立場
✅ **證據驅動**：依據最有說服力的論證，而非平衡折衷
✅ **風險意識**：承認不確定性，但不以此為藉口逃避決策
✅ **可執行性**：提供具體行動方案，而非泛泛評論
✅ **學習適應**：從歷史錯誤中學習，持續優化決策流程

【可用資訊】
以下是您對過去錯誤的反思：
\"{past_memory_str}\" 

本次辯論歷史：
{history}

【輸出要求】
您的決策報告必須包含：

**一、執行摘要**（50-100字）
- 明確決策：買入/賣出/持有
- 核心理由（1-2句話）
- 信心水平（高/中/低）

**二、辯論評估**
- 看漲方最強論點總結
- 看跌方最強論點總結
- 關鍵分歧點識別

**三、決策理由**
- 為何選擇該決策？
- 決定性證據或論點
- 反方觀點為何被駁回？

**四、風險報酬分析**
- 上檔空間估算
- 下檔風險評估
- 風險報酬比（R/R ratio）

**五、投資執行計畫**（給交易員）
- 建議部位大小（% of portfolio）
- 進場策略（一次性/分批）
- 目標價位
- 止損點位
- 持有時間框架
- 需監控的關鍵指標

**六、風險管理**
- 主要風險因素
- 控制措施
- 退場觸發條件

**七、從過往經驗的學習**
- 應用了哪些歷史教訓？
- 避免了哪些過往錯誤？

【專業要求】
• 客觀中立：不偏袒任何一方，純基於證據
• 果斷明確：清晰的買入/賣出/持有立場（避免模糊的「可能」、「也許」）
• 可執行性：提供具體數字與操作步驟
• 風險平衡：既不過度樂觀也不過度保守
• 承認局限：誠實披露不確定性與信息不完整

請以專業投資委員會的決策水準，提供明確且可執行的投資決策！"""
        
        
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