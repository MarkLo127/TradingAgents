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

        # 建立上下文，包含給交易員的指示和投資計畫
        context = {
            "role": "user",
            "content": f"根據分析師團隊的綜合分析，這是一份為 {company_name} 量身定制的投資計畫。該計畫結合了當前技術市場趨勢、宏觀經濟指標和社群媒體情緒的見解。請以此計畫為基礎，評估您的下一個交易決策。\n\n建議的投資計畫：{investment_plan_truncated}\n\n利用這些見解，做出明智且具策略性的決策。",
        }

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