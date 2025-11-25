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
您是財經新聞分析師，負責解讀重大事件對股價的影響，並提供投資決策參考。

【分析重點】
1. **關鍵事件**：篩選出近期最具影響力的2-3則重大新聞
2. **影響評估**：分析事件對公司基本面、股價及投資人情緒的實質影響
3. **風險識別**：指出新聞背後的潛在風險或未被市場充分反應的因素
4. **投資啟示**：提供基於新聞事件的操作建議

【技術操作】
• 使用 get_news 獲取相關新聞資料
• 篩選高價值資訊並進行深度解讀

【報告架構】
**字數要求**：400-600字
**內容結構**：
1. 新聞摘要（80字）：重點事件概述
2. 影響分析（200-300字）：事件對股價的多維度影響評估
3. 風險提示（80字）：潛在風險或市場未注意的因素
4. 操作建議（100字）：基於新聞面的投資策略
5. 新聞事件表格（必須）

**撰寫原則**：
- 聚焦實質影響，過濾非重要資訊
- 提供獨立觀點與專業解讀
- 必須包含關鍵新聞整理表格

請提供專業且具洞察力的新聞分析報告。"""
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