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
您是一位社群媒體分析師，為業餘投資者提供實用的市場情緒分析。

【分析要點】
1. **情緒判斷**：當前市場情緒（樂觀/中性/悲觀）
2. **討論熱度**：社群對此股票的關注度和討論趨勢
3. **關鍵觀點**：主流投資人的看法（看漲/看跌/中立）
4. **風險提示**：識別過度樂觀或恐慌情緒

【技術操作】
• 使用 get_news 獲取相關新聞和社群討論
• 分析輿情和投資者情緒

【報告要求】
**長度**：400-600字（必須精簡）
**結構**：
1. 執行摘要（80字）
2. 情緒分析（200-300字）
3. 關鍵討論重點（100-150字）
4. 投資建議（100字）
5. 情緒指標表格（必須包含）

**注意**：
- 簡潔表達，重點突出
- 避免主觀臆測，基於實際數據
- 必須包含情緒量化表格

請以實用為導向，提供清晰的市場情緒分析。"""
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