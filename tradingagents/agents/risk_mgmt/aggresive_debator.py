# -*- coding: utf-8 -*-
import time
import json
from tradingagents.agents.utils.output_filter import fix_common_llm_errors, validate_and_warn


def create_risky_debator(llm):
    """
    建立一個激進的風險辯論員節點。

    這個節點在風險評估辯論中扮演激進派的角色。
    其目標是積極倡導高回報、高風險的機會，強調大膽的策略和競爭優勢。
    它會專注於潛在的上升空間，並挑戰保守和中立的觀點。

    Args:
        llm: 用於生成回應的語言模型。

    Returns:
        function: 一個代表激進辯論員節點的函式，可在 langgraph 中使用。
    """

    def risky_node(state) -> dict:
        """
        激進辯論員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的風險辯論狀態。
        """
        # 從狀態中獲取風險辯論的相關資訊
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        # 獲取其他辯論者的最新回應
        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        # 從狀態中獲取各類分析報告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        # 獲取交易員的決策
        trader_decision = state["trader_investment_plan"]

        # 移除截斷邏輯以保留完整報告內容
        
        # 建立提示 (prompt)
        prompt = f"""**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**
**嚴格禁止：請勿在回覆中使用任何 emoji 表情符號（如 ✅ ❌ 📊 📈 🚀 等）。**
**請只使用純文字、數字、標點符號和必要的 Unicode 符號（如 ↑ ↓ ★ ●等）。**

【專業身份】
您是積極型風險策略師，主張追求高報酬機會，評估上檔潛力。**您必須採取極度激進立場，全力追求最大報酬潛力，並強力反駁保守派的過度謹慎。**

【論證重點】
1. **上檔空間**：量化分析最佳情境下的報酬潛力，放大獲利想像空間
2. **催化事件**：識別可能帶動股價突破的關鍵因素，強調爆發性成長
3. **成長加速**：評估營收或盈餘成長提速的可能性，找出所有加速跡象
4. **保守迷思**：**強力反駁保守派觀點，指出其過度保守可能錯失的巨大機會成本**
5. **風險容忍**：主張適度承擔風險以換取超額報酬

【可用資訊】
- 交易員計畫：{trader_decision}
- 各類報告：{market_research_report}, {sentiment_report}, {news_report}, {fundamentals_report}
- 辯論歷史：{history}
- 對手觀點：{current_safe_response}, {current_neutral_response}

【輸出要求】
**字數要求**：**800-1500字**
**嚴格遵守字數限制，少於800字或超過1500字的報告將被退回**
**內容結構**：
1. 核心主張（150字以上）：清晰且強勢地陳述積極策略的理由，展現必勝信心
2. 機會分析（450-500字）：詳細論證上檔潛力，層層推進論述
3. 反駁保守（100字以上）：**激進地反駁保守派的擔憂，質疑其過度謹慎與縮手縮腳**
4. 操作建議（100字以上）：明確的激進部位建議，鼓勵大膽進場

**撰寫原則**：
- **極度激進**：採取最樂觀立場，追求最大報酬
- **強力反駁**：對保守派論點窮追猛打，揭露其過度謹慎的機會成本
- 量化評估，避免空泛樂觀，但解讀偏向樂觀
- 直接回應風險疑慮，但強調機會遠大於風險
- 鼓勵承擔合理風險以換取超額報酬

**結尾提示**：
請在報告最後加上以下結尾：
「---
⚡ **本報告為積極型風險策略分析，立場追求高報酬機會。建議搭配保守與平衡觀點綜合研判。高報酬伴隨高風險，請謹慎評估。**」

請提供專業且具說服力的積極策略分析。"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)
        
        # CRITICAL FIX: Apply output filtering
        response.content = fix_common_llm_errors(response.content)
        validate_and_warn(response.content, "Aggressive_Debator")

        # 格式化論點
        argument = f"激進分析師：{response.content}"

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",  # 記錄最新的發言者
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node