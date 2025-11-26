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
            """智能截斷文本到指定字符數，在句子邊界處截斷"""
            if len(text) <= max_chars:
                return text
            
            # 在max_chars附近尋找句子結束標記
            truncated = text[:max_chars]
            
            # 尋找最後一個句號、換行或逗號
            for delimiter in ['。', '\n', '，', '、', ' ']:
                last_pos = truncated.rfind(delimiter)
                if last_pos > max_chars * 0.8:  # 至少保留80%的內容
                    return text[:last_pos + 1] + "\n\n...(為控制長度已精簡)"
            
            # 如果找不到合適的分隔符，直接在字符處截斷
            return truncated + "...(為控制長度已精簡)"
        
        
        # 截斷各類報告以控制 token 使用量
        # 增加限制以確保 800+ 字的報告不被截斷
        market_research_report_truncated = truncate_text(market_research_report, 2000)
        sentiment_report_truncated = truncate_text(sentiment_report, 2000)
        news_report_truncated = truncate_text(news_report, 2500)
        fundamentals_report_truncated = truncate_text(fundamentals_report, 2000)
        investment_plan_truncated = truncate_text(investment_plan, 2000)

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
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是交易執行專家，負責將投資決策轉化為具體可執行的交易計畫。

【職責】
1. **整合決策**：綜合研究團隊與風控團隊的建議，形成統一執行方案
2. **制定計畫**：明確買入/賣出/持有的執行細節與時機
3. **風險管理**：設定清晰的進出場與停損參數，確保風控到位

【可用資訊】
- 投資計畫：{investment_plan_truncated}
- 過去反思：{past_memory_str}

【輸出要求】
**字數要求**：**至少800字以上**
**內容結構**：
1. 執行摘要（150字以上）：最終決策與核心理由的清晰陳述
2. 決策整合（150字以上）：研究與風控觀點的平衡整合過程
3. 交易計畫（400字以上）：
   - 進場策略：具體價位區間與進場時機
   - 部位規模：資金配置比例與分批策略
   - 目標價位：獲利了結點與階段性目標
   - 停損設定：風險控制線與觸發條件
4. 監控機制（100字以上）：關鍵監控指標與調整觸發條件

**撰寫原則**：
- 決策明確，參數具體，避免模糊表述
- 可執行性強，提供清晰的操作步驟
- 風險控制完善，確保每個環節都有風控措施
- 兼顧機會把握與風險管理的平衡

**結尾提示**：
請在報告最後加上以下內容：
「---
💼 **本報告為交易執行計畫，整合研究與風控決策後制定。執行前需確認市場狀況，嚴格遵守風控參數。投資有風險，請謹慎評估。**」

**重要**：請以「最終交易提案：**買入/持有/賣出**」結束回應！"""

        # 建立傳送給 LLM 的訊息列表
        messages = [
            {
                "role": "system",
                "content": f"""您是一位分析市場數據以做出投資決策的交易代理。根據您的分析，提供具體的買入、賣出或持有建議。以堅定的決策結束，並始終以「最終交易提案：**買入/持有/賣出**」來結束您的回應，以確認您的建議。不要忘記利用過去決策的教訓來從錯誤中學習。以下是您在類似情況下交易的一些反思和學到的教訓：{past_memory_str}""",
            },
            {
                "role": "user",
                "content": prompt,
            },
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