from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news, get_global_news
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    """
    建立一個新聞分析師節點。

    Args:
        llm: 用於分析的語言模型。

    Returns:
        一個處理新聞分析的節點函式。
    """
    def news_analyst_node(state):
        """
        分析最近的新聞和趨勢。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含新聞分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            get_news,
            get_global_news,
        ]

        system_message = (
            "您是一位新聞研究員，負責分析過去一週的近期新聞和趨勢。請撰寫一份關於當前世界狀況的綜合報告，該報告與交易和宏觀經濟相關。使用可用的工具：get_news(query, start_date, end_date) 用於公司特定或有針對性的新聞搜索，以及 get_global_news(curr_date, look_back_days, limit) 用於更廣泛的宏觀經濟新聞。不要只說趨勢好壞參半，請提供詳細且精細的分析和見解，以幫助交易員做出決策。"
            + """ 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點，使其井然有序且易於閱讀。"""
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
                    "供您參考，目前日期是 {current_date}。我們正在關注的公司是 {ticker}",
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
            "news_report": report,
        }

    return news_analyst_node