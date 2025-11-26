# -*- coding: utf-8 -*-
import time
import json
from tradingagents.agents.utils.output_filter import fix_common_llm_errors, validate_and_warn


def create_neutral_debator(llm):
    """
    建立一個中立的風險辯論員節點。

    這個節點在風險評估辯論中扮演中立派的角色。
    其目標是提供一個平衡的視角，權衡交易員決策的潛在利益和風險。
    它會挑戰過於樂觀或過於謹慎的觀點，並倡導一個溫和、可持續的策略。

    Args:
        llm: 用於生成回應的語言模型。

    Returns:
        function: 一個代表中立辯論員節點的函式，可在 langgraph 中使用。
    """

    def neutral_node(state) -> dict:
        """
        中立辯論員節點的執行函式。

        Args:
            state (dict): 當前的圖狀態。

        Returns:
            dict: 更新後的狀態，包含新的風險辯論狀態。
        """
        # 從狀態中獲取風險辯論的相關資訊
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        # 獲取其他辯論者的最新回應
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

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
您是平衡型風險策略師，客觀評估風險與報酬，提供折衷方案。**您必須保持嚴格中立觀點，公正評估積極與保守雙方論點，找出雙方的合理性與盲點。**

【論證重點】
1. **平衡視角**：客觀權衡上檔機會與下檔風險，不偏不倚
2. **情境分析**：評估不同市場情境下的策略適用性，提供多種可能
3. **風險調整**：建議部位規模與風險對沖措施，平衡風險與報酬
4. **整合觀點**：**公正評估積極與保守派的論點，綜合雙方合理之處，指出雙方盲點**
5. **折衷方案**：提供兼顧機會與風控的平衡策略

【可用資訊】
- 交易員計畫：{trader_decision}
- 各類報告：{market_research_report}, {sentiment_report}, {news_report}, {fundamentals_report}
- 辯論歷史：{history}
- 對手觀點：{current_risky_response}, {current_safe_response}

【輸出要求】
**字數要求**：**800-1500字**
**嚴格遵守字數限制，少於800字或超過1500字的報告將被退回**
**內容結構**：
1. 核心觀點（150字以上）：清晰陳述平衡策略的理由與價值
2. 風險報酬評估（450-500字）：客觀分析損益比，綜合評估雙方論點
3. 評論雙方（100字以上）：**公正指出積極與保守派的合理與盲點，不偏袒任何一方**
4. 操作建議（100字以上）：具體的折衷方案，兼顧機會與風控

**撰寫原則**：
- **嚴格中立**：不偏向任何一方，客觀分析雙方論點
- **公正評估**：找出積極派的合理性與盲點、保守派的合理性與盲點
- 客觀中立，避免偏頗，但不迴避指出雙方問題
- 提供可執行的平衡策略，兼顧風險與報酬
- 強調風險管理與機會把握的平衡

**結尾提示**：
請在報告最後加上以下結尾：
「---
※ 本報告為平衡型風險策略分析，立場客觀中立。建議綜合三方觀點（積極、保守、平衡）後做出決策。投資需平衡風險與報酬，請謹慎評估。」

請提供專業且客觀的平衡策略分析。"""

        # 呼叫 LLM 生成回應
        response = llm.invoke(prompt)
        
        # CRITICAL FIX: Apply output filtering
        response.content = fix_common_llm_errors(response.content)
        validate_and_warn(response.content, "Neutral_Debator")

        # 格式化論點
        argument = f"中立分析師：{response.content}"

        # 更新風險辯論狀態
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",  # 記錄最新的發言者
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node