from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):
    """
    建立一個市場分析師節點。

    Args:
        llm: 用於分析的語言模型。

    Returns:
        一個處理市場分析的節點函式。
    """

    def market_analyst_node(state):
        """
        分析市場數據和技術指標。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含市場分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)  # 使用真實公司名稱，fallback到ticker

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是一位技術分析師，為業餘投資者提供實用的市場分析。

【分析要點】
1. **趨勢判斷**：明確判斷當前趨勢（多頭/空頭/盤整）
2. **技術指標**：選擇3-5個最重要的指標分析
   - 建議指標：50日/200日均線、MACD、RSI、布林帶、ATR
3. **關鍵價位**：標示主要支撐和阻力位
4. **交易建議**：給出明確的進場、出場和止損建議

【技術操作】
• 使用 get_stock_data 獲取價格數據
• 使用 get_indicators 計算所需指標
• 基於數據進行分析

【報告要求】
**長度**：500-800字（必須精簡）
**結構**：
1. 執行摘要（100字）
2. 趨勢與指標分析（300-400字）
3. 支撐阻力位（100字）
4. 交易建議（100-200字）
5. 數據表格（必須包含）

**注意**：
- 使用簡潔語言，避免過度專業術語
- 重點突出，不要冗長描述
- 必須包含關鍵數據表格總結

請以實用為導向，提供清晰易懂的技術分析。"""
            + """ 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點。"""
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
                    "供您參考，目前日期是 {current_date}。我們想關注的公司是 {company_name} （股票代碼：{ticker}）",
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
        # 當LLM調用工具時（tool_calls不為空），不更新報告
        # 當LLM返回最終分析時（tool_calls為空），保存完整報告
        report = state.get("market_report", "")  # 保持現有報告
        
        if len(result.tool_calls) == 0:
            # 沒有工具調用，這是最終的分析報告
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node