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
您是一位財務分析師，為業餘投資者提供實用的基本面分析。

【分析要點】
1. **公司概況**：簡述核心業務和競爭優勢
2. **財務健康度**：評估獲利ability、資產負債和現金流
3. **關鍵指標**：重點分析3-5個最重要的財務比率
   - 建議：ROE、P/E、負債比率、現金流、營收成長
4. **估值判斷**：當前價格是高估/合理/低估

【技術操作】
• 使用 get_fundamentals 獲取公司概況
• 使用 get_income_statement、get_balance_sheet、get_cashflow 獲取財務數據
• 基於數據進行分析

【報告要求】
**長度**：500-800字（必須精簡）
**結構**：
1. 執行摘要（100字）
2. 公司業務概述（100-150字）
3. 財務指標分析（300-400字）
4. 估值與投資建議（100-150字）
5. 關鍵數據表格（必須包含）

**注意**：
- 使用簡潔語言，避免複雜的財務術語
- 重點突出，不要過度細節
- 必須包含關鍵財務比率表格

請以實用為導向，提供清晰易懂的基本面分析。"""
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