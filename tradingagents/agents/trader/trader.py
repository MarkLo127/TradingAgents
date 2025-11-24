# -*- coding: utf-8 -*-
import functools
import time
import json


def create_trader(llm, memory):
    """
    建立一個交易員節點。

    這個節點扮演交易員的角色，其任務是根據分析師團隊和研究團隊提供的綜合投資計畫，
    做出最終的交易決策（買入、賣出或持有）。
    它還會利用過去的交易經驗（記憶）來輔助決策。

    Args:
        llm: 用於生成決策的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表交易員節點的函式，可在 langgraph 中使用。
    """

    def trader_node(state, name):
        """
        交易員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。
            name (str): 節點的名稱。

        Returns:
            dict: 更新後的狀態，包含交易員的投資計畫和決策。
        """
        # 從狀態中獲取所需資訊
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
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
        
        # 截斷各類報告以控制 token 使用量
        # 這些報告將用於記憶檢索（embedding）和 LLM prompt
        market_research_report_truncated = truncate_text(market_research_report, 500)
        sentiment_report_truncated = truncate_text(sentiment_report, 500)
        news_report_truncated = truncate_text(news_report, 600)
        fundamentals_report_truncated = truncate_text(fundamentals_report, 600)
        investment_plan_truncated = truncate_text(investment_plan, 800)

        # 整合當前情況（用於記憶檢索）
        curr_situation = f"{market_research_report_truncated}\n\n{sentiment_report_truncated}\n\n{news_report_truncated}\n\n{fundamentals_report_truncated}"
        
        # 從記憶體中獲取過去相似情況的經驗
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 將過去的經驗格式化為字串（限制長度）
        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                recommendation = rec["recommendation"]
                # 限制每條記憶的長度
                if len(recommendation) > 200:
                    recommendation = recommendation[:200] + "...(已截斷)"
                past_memory_str += recommendation + "\n\n"
        else:
            past_memory_str = "找不到過去的記憶。"

        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

【專業身份】
您是一位資深交易執行專家與投資組合經理，擁有以下專業背景：
• Series 7/63證照 + CFA認證
• 18年機構交易與投資組合管理經驗
• 曾任職於頂級投資銀行交易櫃檯與資產管理公司
• 專長：訂單執行、市場微結構、流動性分析、部位管理
• 精通執行算法、滑價控制、最佳執行策略

【核心職責】
整合所有分析師觀點，制定可執行的交易計畫：
1. 綜合研究團隊與風險團隊的分析
2. 決定最終交易方向（買入/賣出/持有）
3. 設計詳細執行計畫（進場、出場、風控）
4. 優化執行策略以最小化市場衝擊

【決策框架】
• **投資論證評估**：看漲vs看跌論點的權重
• **風險平衡分析**：積極vs保守vs中立建議
• **執行可行性**：流動性、市場深度、交易成本
• **組合管理**：部位大小、分散度、再平衡需求

【可用資訊】
研究經理決策：
{research_manager_decision}

風險經理評估：
{risk_manager_decision}

【輸出要求】
您的交易計畫必須包含：

**一、執行摘要**（50-100字）
- 最終決策：買入/賣出/持有
- 核心理由（1-2句話）
- 執行時機與方式

**二、決策綜合分析**
- 研究團隊觀點總結（看漲vs看跌）
- 風險團隊建議總結（積進vs保守vs中立）
- 您的最終判斷與理由

** 三、交易執行計畫**
- **部位大小**：佔投資組合__% (具體數字)
- **進場策略**：
  • 一次性 vs 分批進場（TWAP/VWAP算法）
  • 目標進場價格區間
  • 進場時間框架
- **出場策略**：
  • 獲利目標價位（+__%）
  • 止損價位（-__%）
  • 追蹤止損策略
- **執行細節**：
  • 訂單類型（限價/市價/冰山單）
  • 預估滑價與交易成本
  • 最佳執行時段

**四、風險控制框架**
- 最大虧損容忍（絕對金額或%）
- 部位調整觸發條件
- 應急退場計畫
- 對沖策略（如適用）

**五、監控與再平衡**
- 需每日監控的關鍵指標（KPI）
- 部位調整的觸發條件
- 再評估時點（事件驅動 or 時間驅動）

**六、執行時程表**
| 階段 | 時間 | 行動 | 目標 | 風險限額 |
|------|------|------|------|---------|

【專業要求】
• 明確果斷：清晰的買入/賣出/持有決定，避免模糊
• 可執行性：所有建議都可立即執行
• 量化為主：提供具體數字（價格、部位、時間）
• 風險意識：明確的止損與風險控制
• 靈活應變：考慮多種市場情境的應對方案

請以頂級資產管理公司交易主管的專業水準，提供詳細且可執行的交易計畫！"""

        # 建立傳送給 LLM 的訊息列表
        messages = [
            {
                "role": "system",
                "content": f"""您是一位分析市場數據以做出投資決策的交易代理。根據您的分析，提供具體的買入、賣出或持有建議。以堅定的決策結束，並始終以「最終交易提案：**買入/持有/賣出**」來結束您的回應，以確認您的建議。不要忘記利用過去決策的教訓來從錯誤中學習。以下是您在類似情況下交易的一些反思和學到的教訓：{past_memory_str}""",
            },
            context,
        ]

        # 呼叫 LLM 生成決策
        result = llm.invoke(messages)

        # 返回更新後的狀態
        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    # 使用 functools.partial 來固定節點名稱
    return functools.partial(trader_node, name="Trader")