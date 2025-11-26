from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    """
    建立一個社群媒體分析師節點。

    Args:
        llm: 用於分析的語言模型。

    Returns:
        一個處理社群媒體分析的節點函式。
    """
    def social_media_analyst_node(state):
        """
        分析社群媒體貼文、近期公司新聞和公眾情緒。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含情緒分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)  # 使用真實公司名稱，fallback到ticker

        tools = [
            get_news,
        ]

        system_message = (
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**
**嚴格禁止：請勿在回覆中使用任何 emoji 表情符號（如 ✅ ❌ 📊 📈 🚀 等）。**
**請只使用純文字、數字、標點符號和必要的 Unicode 符號（如 ↑ ↓ ★ ●等）。**

【專業身份】
您是市場情緒分析專家，負責解讀社群媒體與輿論氛圍對股價的潛在影響。

【分析重點】
1. **情緒基調**：評估當前市場情緒狀態（樂觀/中性/悲觀）及其強度
2. **討論熱度**：識別主流話題與關注焦點，判斷輿論方向
3. **投資人結構**：觀察散戶與機構觀點的分歧或共識
4. **極端訊號**：檢視是否出現非理性樂觀或恐慌情緒

【技術操作】
• 使用 get_news 獲取相關新聞與社群討論資料
• 分析輿情傾向與討論熱度

【報告架構】
**字數要求**：**800-1500字（不含表格）**
**嚴格遵守字數限制，少於800字或超過1500字的報告將被退回**

**內容結構**：
1. 情緒概要（150字以上）：市場氛圍與情緒指標
2. 輿情分析（400-450字）：主要討論議題與觀點分布
3. 關鍵洞察（100字以上）：情緒極值或轉折訊號
4. 投資含義（150字以上）：情緒面對操作策略的啟示
5. 情緒數據表格（必須）

**撰寫原則**：
- **兼具專業與易懂**：使用專業術語的同時，請用生活化的語言讓一般投資人也能理解
- **舉例說明**：在解讀情緒指標時，適時加入白話文說明（例如：「恐慌貪婪指數達78，就像溫度計顯示發燒，代表市場過熱需要降溫」）
- 客觀分析，避免主觀臆測
- 聚焦有價值的情緒訊號
- 必須包含情緒量化數據表格

**結尾提示**：
請在報告最後加上以下結尾：
「---
💬 **本報告為市場情緒分析，建議搭配基本面及技術面綜合研判。投資有風險，請謹慎評估。**」

請提供專業且具洞察力、兼具易讀性的市場情緒分析報告。"""
            + """ 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點。""",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一個樂於助人的人工智慧助理，與其他助理協同工作。"
                    " 使用提供的工具來逐步回答問題。"
                    " 如果您無法完全回答，沒關係；另一個擁有不同工具的助理會在您中斷的地方提供幫助。盡您所能取得進展。"
                    " 如果您或任何其他助理有最終交易提案：**買入/持有/賣出** 或可交付成果，"
                    " 請在您的回覆前加上「最終交易提案：**買入/持有/賣出**」，以便團隊知道停止。"
                    " 您可以使用以下工具：{tool_names}。\n{system_message}"
                    "供您參考，目前日期是 {current_date}。我們目前要分析的公司是 {company_name} （股票代碼：{ticker}）",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=company_name)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        # 報告邏輯修復：只在LLM最終回應時保存報告
        report = state.get("sentiment_report", "")  # 保持現有報告

        if len(result.tool_calls) == 0:
            # 沒有工具調用，這是最終的分析報告
            report = result.content

        return {
            "messages": [result],
            "sentiment_report": report,
        }

    return social_media_analyst_node