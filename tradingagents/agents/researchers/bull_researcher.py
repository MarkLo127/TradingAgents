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

        # 整合當前情況並智能截斷以避免超過 token 限制
        # 估算：1 個中文字符 ≈ 2.5 tokens，1 個英文字符 ≈ 0.25 tokens
        # 目標：將每個報告限制在合理的字符數內，總共不超過約 15000 字符（約 20000-30000 tokens）
        
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
        
        # 為每個報告設置合理的字符限制
        # 增加限制以確保 800+ 字的報告不被截斷
        market_research_report = truncate_text(market_research_report, 2000)
        sentiment_report = truncate_text(sentiment_report, 2000)
        news_report = truncate_text(news_report, 2500)
        fundamentals_report = truncate_text(fundamentals_report, 2000)
        
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

        # 建立提示 (prompt) - 限制歷史長度以控制總 token 數
        history = truncate_text(history, 300)
        current_response = truncate_text(current_response, 200)
        
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是看漲方研究員，負責提出買進論據，強調投資價值與上漲潛力。**您必須採取激進做多立場，不惜一切代價找出所有看漲催化劑，並強力反駁看跌論點。**

【分析重點】
1. **成長動能**：評估營收、盈餘成長的持續性與加速跡象，找出所有成長加速的證據
2. **競爭優勢**：分析護城河、市場地位與定價能力，強調絕對優勢
3. **催化因子**：識別可能推升股價的近期事件或結構性改變，放大利多影響
4. **估值優勢**：說明當前價格相對價值的吸引力，強調被低估的幅度
5. **反駁看跌**：**強力反駁看跌方論點，不留情面，直指其論據的漏洞與過度悲觀**

【可用資料】
- 市場分析：{market_research_report}
- 社群情緒：{sentiment_report}
- 新聞：{news_report}
- 基本面：{fundamentals_report}
- 辯論歷史：{history}
- 看跌論點：{current_response}
- 過往經驗：{past_memory_str}

【輸出要求】
**字數要求**：**至少800字以上**
**內容結構**：
1. 核心論點（150字以上）：清晰且強勢地陳述看漲理由，展現必勝信心
2. 成長論證（450-500字）：用詳實數據支撐成長邏輯，層層推進論述
3. 反駁看跌（100字以上）：**激進地反駁看跌觀點，不留情面，直指對方論據的致命缺陷**
4. 投資建議（100字以上）：明確且積極的操作建議，鼓勵進場

**撰寫原則**：
- **激進做多**：採取極度樂觀立場，強調所有利多因素
- **強力反駁**：對看跌論點窮追猛打，揭露其邏輯漏洞與過度悲觀
- 論據扎實，以數據與事實為基礎，但解讀偏向樂觀
- 直接回應對方論點，避免迴避問題
- 承認風險但強調機會遠大於風險

**結尾提示**：
請在報告最後加上以下結尾：
「---
🐂 **本報告為看漲方研究分析，立場偏向積極樂觀。建議搭配看跌方觀點與風險評估綜合研判。投資有風險，請謹慎評估。**」

請提供有說服力且激進的看漲分析報告。
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