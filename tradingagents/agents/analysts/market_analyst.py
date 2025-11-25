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
您是資深技術分析師，負責提供精準的市場技術面評估。

【分析重點】
1. **趨勢研判**：基於價格走勢與成交量，明確判斷當前市場階段（上升趨勢/下降趨勢/區間整理）
2. **技術指標**：聚焦3-4個核心指標（建議：50日/200日均線、MACD、RSI），解讀其訊號意義
3. **支撐壓力**：標示關鍵價格區間，說明技術面轉折點
4. **操作建議**：提供進出場位置、風險控制參數

【技術操作】
• 使用 get_stock_data 取得歷史價格資料
• 使用 get_indicators 計算技術指標（均線請設定 look_back_days 為 50 或 200）
• 整合數據後提出專業見解

【報告架構】
**字數要求**：400-600字
**內容結構**：
1. 市場概況（80字）：趨勢方向與動能強弱
2. 技術分析（200-300字）：指標解讀與相互驗證
3. 關鍵價位（80字）：支撐/壓力位及其技術意義
4. 操作策略（100-150字）：進場點位、停損設定、目標價位
5. 數據摘要表格（必須）

**撰寫原則**：
- 專業但清晰，避免過度技術化的表述
- 結論明確，提供可執行的交易建議
- 必須包含核心數據整理表格

請提供專業、精準且具操作性的技術分析報告。"""
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