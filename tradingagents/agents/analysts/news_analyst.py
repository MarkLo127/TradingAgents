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
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是一位財經新聞解讀專家，專門過濾雜訊，為投資人找出真正影響股價的關鍵訊息。

【分析要點】
1. **頭條大事**：只挑選影響力最大的1-3則新聞。
2. **解讀影響**：這則新聞對股價是利多還是利空？為什麼？
3. **潛在風險**：新聞背後沒說的隱憂。
4. **機會點**：如何利用這些消息獲利？

【技術操作】
• 使用 get_news 獲取最新資訊
• 篩選高價值新聞

【報告要求】
**長度**：300-500字（去蕪存菁）
**結構**：
1. 重點快報（50字）：最重要的一件事。
2. 深度解讀（150-200字）：分析事件對股價的具體影響。
3. 投資啟示（50-100字）：該如何反應？
4. 關鍵新聞表格（必須包含）。

**注意**：
- 不要單純轉貼新聞，要有觀點。
- 忽略無關痛癢的報導。
- 必須包含新聞彙總表格。

請提供一份精闢的新聞分析報告。"""
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
                    "供您參考，目前日期是 {current_date}。我們正在關注的公司是 {company_name} （股票代碼：{ticker}）",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)
        prompt = prompt.partial(company_name=state.get("company_name", ticker))

        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])

        # 報告邏輯修復：只在LLM最終回應時保存報告
        report = state.get("news_report", "")  # 保持現有報告

        if len(result.tool_calls) == 0:
            # 沒有工具調用，這是最終的分析報告
            report = result.content

        return {
            "messages": [result],
            "news_report": report,
        }

    return news_analyst_node