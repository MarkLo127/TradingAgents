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
        company_name = state["company_of_interest"]

        tools = [
            get_news,
        ]

        system_message = (
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。請勿使用英文、簡體中文或其他語言。**

您是一位社群媒體和公司特定新聞研究員/分析師，負責分析特定公司過去一週的社群媒體貼文、近期公司新聞和公眾情緒。您將獲得一個公司名稱，您的目標是撰寫一份全面的長篇報告，詳細說明您在查看社群媒體以及人們對該公司的評論、分析人們每天對公司的感受的情緒數據以及查看近期公司新聞後，對該公司當前狀況的分析、見解以及對交易員和投資者的影響。使用 get_news(query, start_date, end_date) 工具搜索公司特定的新聞和社群媒體討論。盡可能查看所有可能的來源，從社群媒體到情緒再到新聞。不要只說趨勢好壞參半，請提供詳細且精細的分析和見解，以幫助交易員做出決策。"""
            + """ 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點，使其井然有序且易於閱讀。""",
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
                    "供您參考，目前日期是 {current_date}。我們目前要分析的公司是 {ticker}",
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
            "sentiment_report": report,
        }

    return social_media_analyst_node