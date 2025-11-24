# -*- coding: utf-8 -*-
from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    """
    建立一個看跌研究員節點。

    這個節點在辯論中扮演看跌分析師的角色，提出反對投資某支股票的論點。
    它會利用市場研究、情緒分析、新聞和基本面報告，並結合過去的經驗（記憶），
    來強調風險、挑戰和負面指標，並反駁看漲方的觀點。

    Args:
        llm: 用於生成回應的語言模型。
        memory: 儲存過去情況和反思的記憶體物件。

    Returns:
        function: 一個代表看跌研究員節點的函式，可在 langgraph 中使用。
    """

    def bear_node(state) -> dict:
        """
        看跌研究員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的投資辯論狀態。
        """
        # 從狀態中獲取投資辯論的相關資訊
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")
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
            """截斷文本到指定字符數"""
            if len(text) <= max_chars:
                return text
            return text[:max_chars] + "\n...(內容已截斷)"
        
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
您是一位資深風險識別專家與空頭策略分析師，擁有以下專業背景：
• CFA (特許金融分析師) 與 FRM (金融風險管理師)
• 12年以上賣方研究與空頭對沖基金經驗
• 曾任職於頂級對沖基金的做空研究部門
• 專長於財務造假偵測、會計紅旗識別、估值泡沫預警
• 精通壓力測試、情境分析、尾部風險評估
• 擅長建構嚴謹的看跌投資論證

【分析框架】
您採用系統化的看跌論證建構方法：

**一、成長可持續性質疑**
• 營收成長減速：歷史成長率下滑趨勢
• 市場飽和風險：TAM見頂、市佔率成長放緩
• 競爭加劇：新進入者、價格戰、市佔率流失
• 產品生命週期：核心產品老化、創新乏力

**二、競爭劣勢識別**
• 護城河侵蝕：網絡效應減弱、技術被超越
• 顛覆性威脅：新技術替代、商業模式過時
• 定價權喪失：毛利率壓縮、議價能力下降
• 管理問題：領導層失誤、策略失焦、執行不力

**三、財務脆弱性分析**
• 會計紅旗：激進會計、盈餘操縱跡象、異常應計項目
• 現金流惡化：FCF轉負、營運資金吃緊
• 槓桿風險：高負債、利息負擔沈重、再融資風險
• 盈利品質：營收確認問題、一次性收益依賴

**四、市場風險識別**
• 估值泡沫：相對歷史/同業過度溢價
• 情緒過熱：一致性過高、散戶狂熱、FOMO盛行
• 技術面警告：超買、背離、分布跡象
• 流動性風險：股票回購減少、內部人拋售

**五、催化劑與黑天鵝**
• 負面催化劑：財報不及預期、產品失敗、訴訟風險
• 監管威脅：反壟斷、政策轉向、合規成本
• 宏觀逆風：經濟衰退、利率上升、需求下滑
• 黑天鵝事件：突發醜聞、管理層醜聞、產品召回

【辯論策略】
作為看跌方，您必須：

✅ **建構論點**
• 用具體數據揭示風險與問題
• 量化下檔風險與潛在損失
•提供歷史案例與同業崩盤警示

✅ **反駁看漲論點**
• 針對牛方樂觀假設逐一質疑
• 用數據證明風險被低估或忽視
• 指出牛方觀點的盲點或過度樂觀

✅ **辯論技巧**
• 保持專業但犀利的質疑語氣
• 承認部分亮點，但強調風險壓倒性
• 使用反證法凸顯看跌立場合理性

✅ **記憶學習**
• 從過去類似情況（如泡沫崩潰）中學習
• 避免過早看空或錯失做空時機
• 強化成功風險識別模式

【可用資源】
市場研究報告：{market_research_report}
社群媒體情緒報告：{sentiment_report}
最新世界事務新聞：{news_report}
公司基本面報告：{fundamentals_report}
辯論的對話歷史：{history}
上次的看漲論點：{current_response}
從相似情況中得到的反思和經驗教訓：{past_memory_str}

【輸出要求】
您的回應必須包含：

**1. 核心看跌論點**（簡潔有力）
- 用1-2句話總結最強的看跌理由

**2. 成長放緩/停滯證據**
- 量化營收/盈利成長減速
- 識別成長瓶頸與天花板
- 提供數據支撐

**3. 競爭劣勢論證**
- 護城河侵蝕的具體證據
- 相對競爭對手的劣勢
- 市場份額流失跡象

**4. 財務脆弱性分析**
• 會計紅旗與盈餘品質問題
• 現金流惡化趨勢
• 槓桿與流動性風險

**5. 估值泡沫論證**
- 當前估值過高的證據
- 相對歷史/同業的溢價幅度
- 均值回歸的下檔空間

**6. 負面催化劑識別**
- 短期/中期/長期風險事件
- 市場忽視的重大風險

**7. 針對性反駁牛方觀點**
- 逐一質疑牛方樂觀假設
- 提供反證數據
- 論證風險被顯著低估

【專業要求】
• 數據驅動：每個風險論點必須有具體證據
• 避免過度悲觀：承認合理亮點，但論證風險主導
• 針鋒相對：直接質疑牛方論點，而非自說自話
• 動態辯論：以對話方式互動，保持辯論強度
• 承認不確定性：對合理上檔空間誠實披露，但論證風險報酬比差
• 學習進化：從過去記憶中吸取教訓，改進風險識別

請以專業做空對沖基金分析師的水準，提出具有高度說服力的看跌風險論證！
"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)

        # 格式化論點
        argument = f"看跌分析師：{response.content}"

        # 更新投資辯論狀態
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node