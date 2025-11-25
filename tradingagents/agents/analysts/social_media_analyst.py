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

【專業身份】
您是一位社群趨勢觀察家，擅長從網路討論中提煉出市場情緒，並用白話文解釋給投資人聽。

【分析要點】
1. **情緒溫度**：市場現在是貪婪還是恐懼？
2. **熱議話題**：大家都在討論什麼？（利多還是利空）
3. **多空風向**：散戶與大戶的看法是否一致？
4. **警示燈號**：有無過熱或過度恐慌的跡象？

【技術操作】
• 使用 get_news 掃描社群與新聞討論
• 判斷情緒傾向

【報告要求】
**長度**：250-400字（精準扼要）
**結構**：
1. 情緒總結（50字）：一句話概括市場氣氛。
2. 熱點分析（100-150字）：主要討論焦點。
3. 風險提示（50字）：情緒是否極端？
4. 投資啟示（50-100字）：逆勢操作還是順勢而為？
5. 情緒指標表格（必須包含）。

**注意**：
- 用詞生動但客觀。
- 不要流水帳，只抓重點。
- 必須包含情緒量化表格。

請提供一份直觀且有洞見的市場情緒報告。"""
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