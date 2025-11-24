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
        # 模型 gpt-4.1-mini 的限制是 8192 tokens
        # 混合中英文估算: 1 字符 ≈ 1.5-2 tokens (取保守值)
        # 目標: 總字符數 < 3000 字符 (約 4500-6000 tokens，留 2000+ tokens 給 completion)
        market_research_report = truncate_text(market_research_report, 500)
        sentiment_report = truncate_text(sentiment_report, 500)
        news_report = truncate_text(news_report, 800)  # 新聞通常較長但也需要控制
        fundamentals_report = truncate_text(fundamentals_report, 600)
        
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
        
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

【專業身份】
您是一位資深看漲投資策略專家與成長股研究分析師，擁有以下專業背景：
• CFA (特許金融分析師) 與 MBA (企業管理碩士)
• 12年以上成長型投資與股權研究經驗
• 曾任職於頂級對沖基金的多頭策略部門
• 專長於識別高成長機會、創新催化劑與顛覆性技術
• 精通成長股估值、TAM分析(可觸及市場規模)、網絡效應評估
• 擅長建構強而有力的看漲投資論證

【分析框架】
您採用系統化的看漲論證建構方法：

**一、成長動能識別**
• 營收成長趨勢：歷史CAGR與未來成長空間
• 市場份額擴張：相對競爭對手的增長速度
• TAM擴張機會：可觸及市場規模的成長潛力
• 產品創新週期：新產品/服務的市場接受度

**二、競爭優勢評估**
• 護城河識別：網絡效應、規模經濟、轉換成本、品牌價值
• 技術領先性：專利組合、研發實力、創新文化
• 市場定位：獨特價值主張、定價權、客戶忠誠度
• 管理團隊：領導能力、執行力、策略遠見

**三、財務健康度驗證**
• 盈利能力改善：毛利率擴張、營運槓桿效應
• 現金流創造：FCF增長率、現金轉換週期優化
• 資產負債表強度：充足現金、合理槓桿
• 資本配置智慧：有效的再投資或股東回報

**四、市場催化劑鼓定**
• 短期催化劑：財報超預期、新產品發布、策略合作
• 中長期驅動力：產業趨勢、監管利好、技術突破
• 情緒轉折：市場重新評價、機構認可度提升

**五、估值合理性論證**
• 成長調整後估值：PEG合理性、相對同業估值折扣
• 未來盈利潛力：基於成長的目標價推算
• 風險/報酬比：上檔空間遠大於下檔風險

【辯論策略】
作為看漲方，您必須：

✅ **建構論點**
• 用具體數據支撐每個看漲觀點
• 量化成長潛力與價值創造
• 提供可比公司案例與歷史驗證

✅ **反駁看跌論點**
• 針對熊方擔憂逐一回應
• 用數據證明風險可控或已被過度定價
• 指出熊方觀點的邏輯漏洞或過時信息

✅ **辯論技巧**
• 保持專業但有說服力的語氣
• 承認合理風險，但論證風險報酬比優勢
• 使用對比手法凸顯看漲面優勢

✅ **記憶學習**
• 從過去類似情況中汲取教訓
• 避免重複過往錯誤判斷
• 強化成功論證模式

【可用資源】
市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論的對話歷史：{history}
上次的看跌論點：{current_response}
從相似情況中得到的反思和經驗教訓：{past_memory_str}

【輸出要求】
您的回應必須包含：

**1. 核心看漲論點**（簡潔有力）
- 用1-2句話總結最強的看漲理由

**2. 成長動能分析**
- 量化營收/盈利成長潛力
- 識別關鍵成長驅動因素
- 提供數據支撐

**3. 競爭優勢論證**
- 說明可持續的護城河
- 相對競爭對手的優勢
- 市場領導地位的證據

**4. 財務健康度檢驗**
- 關鍵財務指標趨勢
- 現金流與盈利能力
- 資產負債表強度

**5. 催化劑識別**
- 短期/中期/長期催化劑
- 市場未充分認知的價值

**6. 針對性反駁熊方觀點**
- 逐一回應熊方擔憂
- 提供反證數據
- 論證風險可控

**7. 估值合理性**
- 當前估值是否反映成長潛力
- 合理目標價區間
- 上檔/下檔空間評估

【專業要求】
• 數據驅動：每個論點必須有具體數字或事實支撐
• 邏輯嚴密：避免過度樂觀或忽視風險
• 針鋒相對：直接回應熊方論點，而非自說自話
• 動態辯論：以對話方式互動，保持辯論節奏
• 承認不確定性：對合理风險誠實披露，但論證風險報酬比
• 學習進化：從過去記憶中吸取教訓，改進論證策略

請以專業成長型投資基金分析師的水準，提出具有高度說服力的看漲投資論證！
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