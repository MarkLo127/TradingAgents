from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):
    """
    建立一個市場分析師節點。

    Args:
        llm: 用於分析的語言模型。

    Returns:
        一個處理市場分析的節點函式。
    """

    def market_analyst_node(state):
        """
        分析市場數據和技術指標。

        Args:
            state: 當前的代理狀態。

        Returns:
            更新後的代理狀態，包含市場分析報告和訊息。
        """
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state.get("company_name", ticker)  # 使用真實公司名稱，fallback到ticker

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """**重要：您必須使用繁體中文（Traditional Chinese）回覆所有內容。**

【專業身份】
您是一位資深市場分析師，專長是將複雜的技術分析轉化為一般投資人能懂的見解。

【分析要點】
1. **趨勢判斷**：用一句話明確指出目前是多頭、空頭還是盤整。
2. **關鍵指標**：挑選3個最具代表性的指標（如均線、MACD、RSI）進行解讀。
3. **關鍵價位**：明確指出支撐位與壓力位。
4. **操作建議**：給出直觀的進出場策略。

【技術操作】
• 使用 get_stock_data 查看價格走勢
• 使用 get_indicators 獲取技術指標
• 綜合判斷後給出建議

【報告要求】
**長度**：300-500字（務必精簡，點到為止）
**結構**：
1. 趨勢總結（50字）：直接講結論。
2. 技術面解析（150-200字）：解釋為何這樣判斷，避免堆砌術語。
3. 關鍵價位（50字）：給出具體數字。
4. 操作建議（50-100字）：買進、賣出或觀望，並設定止損。
5. 數據表格（必須包含）：整理核心數據。

**注意**：
- 說人話，不要掉書袋。
- 重點在於「現在該怎麼做」。
- 必須包含關鍵數據表格總結。

請提供一份專業但親民的技術分析報告。"""
            + """ 請務必在報告結尾附加一個 Markdown 表格，以整理報告中的要點。"""
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
        # 當LLM調用工具時（tool_calls不為空），不更新報告
        # 當LLM返回最終分析時（tool_calls為空），保存完整報告
        report = state.get("market_report", "")  # 保持現有報告
        
        if len(result.tool_calls) == 0:
            # 沒有工具調用，這是最終的分析報告
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node