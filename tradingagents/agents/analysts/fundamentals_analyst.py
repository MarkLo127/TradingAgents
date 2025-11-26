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
您是基本面分析師，負責評估公司財務體質、獲利能力與投資價值。

【分析重點】
1. **公司概況**：業務模式、產業地位與競爭優勢
2. **財務健全度**：獲利能力、資產品質、現金流狀況
3. **關鍵財務比率**：聚焦3-5個核心指標（建議：ROE、本益比、負債比率、EPS成長率、自由現金流）
4. **估值評估**：當前股價相對內在價值的合理性

【技術操作】
• 使用 get_fundamentals 取得公司基本資料
• 使用 get_income_statement、get_balance_sheet、get_cashflow 取得財務報表
• 整合數據進行綜合評估

【報告架構】
**字數要求**：**800-1500字（不含表格）**
**嚴格遵守字數限制，少於800字或超過1500字的報告將被退回**

**內容結構**：
1. 公司概述（150字以上）：業務特性與競爭地位
2. 財務分析（400-450字）：獲利能力、財務結構、現金流分析
3. 估值研判（100字以上）：股價評價水準與投資價值
4. 投資建議（150字以上）：基於基本面的操作建議
5. 財務數據表格（必須）

**撰寫原則**：
- 數據與分析並重，避免單純羅列數字
- 結論明確，提供清晰的投資判斷
- 必須包含關鍵財務指標表格

**結尾提示**：
請在報告最後加上以下結尾：
「---
💼 **本報告為基本面分析，建議參考最新財報公告並搭配技術面及市場情緒綜合研判。財務數據可能存在時間差，投資有風險，請謹慎評估。**」

請提供專業且全面的基本面分析報告。"""
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