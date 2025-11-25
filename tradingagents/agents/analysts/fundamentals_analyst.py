from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_sentiment, get_insider_transactions
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    """
    建立一個基本面分析師節點。

    Args:
        llm: 用於分析的語言模型。

    Returns:
        一個處理基本面分析的節點函式。
    """
    def fundamentals_analyst_node(state):
        """
        分析公司的基本面資訊。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)  # 使用真實公司名稱，fallback到ticker

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是一位基本面投資顧問，擅長將枯燥的財報數據轉化為簡單的投資邏輯。

【分析要點】
1. **體質快篩**：這家公司賺錢嗎？財務安全嗎？
2. **核心指標**：只看最重要的3個數據（如EPS、毛利率、ROE）。
3. **估值位階**：現在股價是便宜、合理還是太貴？
4. **長期展望**：這家公司未來靠什麼成長？

【技術操作】
• 使用 get_fundamentals 等工具獲取數據
• 專注於關鍵財務比率

【報告要求】
**長度**：300-500字（簡單明瞭）
**結構**：
1. 公司簡介（50字）：做什麼的？
2. 財務亮點/隱憂（150-200字）：用白話解釋財務狀況。
3. 估值判斷（50-100字）：現在買划算嗎？
4. 關鍵數據表格（必須包含）。

**注意**：
- 避免堆砌數字，解釋數字背後的意義。
- 結論要明確。
- 必須包含關鍵財務比率表格。

請提供一份深入淺出的基本面分析報告。"""
            + " 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點。"
            + " 使用可用的工具：`get_fundamentals` 用於全面的公司分析，`get_balance_sheet`、`get_cashflow` 和 `get_income_statement` 用於特定的財務報表。"
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
        report = state.get("fundamentals_report", "")  # 保持現有報告

        if len(result.tool_calls) == 0:
            # 沒有工具調用，這是最終的分析報告
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node