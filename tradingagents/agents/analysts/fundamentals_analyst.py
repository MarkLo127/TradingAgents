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
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "您是一位研究員，負責分析一家公司過去一週的基本面資訊。請撰寫一份關於該公司基本面資訊的綜合報告，例如財務文件、公司簡介、基本財務狀況和公司財務歷史，以全面了解公司的基本面資訊，為交易員提供參考。請務必包含盡可能多的細節。不要只說趨勢好壞參半，請提供詳細且精細的分析和見解，以幫助交易員做出決策。"
            + " 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點，使其井然有序且易於閱讀。"
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
                    "供您參考，目前日期是 {current_date}。我們想關注的公司是 {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node