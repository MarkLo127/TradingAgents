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
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """您是一位負責分析金融市場的交易助理。您的角色是從以下列表中為給定的市場狀況或交易策略選擇**最相關的指標**。目標是選擇最多 **8 個**能夠提供互補見解而無冗餘的指標。類別及各類別的指標如下：

移動平均線：
- close_50_sma：50 SMA：中期趨勢指標。用法：識別趨勢方向並作為動態支撐/阻力。提示：它滯後於價格；與更快的指標結合以獲得及時信號。
- close_200_sma：200 SMA：長期趨勢基準。用法：確認整體市場趨勢並識別黃金交叉/死亡交叉設置。提示：它反應緩慢；最適合戰略趨勢確認，而非頻繁的交易入場。
- close_10_ema：10 EMA：反應靈敏的短期平均線。用法：捕捉動能的快速轉變和潛在的入場點。提示：在震盪市場中容易產生噪音；與較長的平均線一起使用以過濾錯誤信號。

MACD 相關：
- macd：MACD：通過 EMA 的差異計算動能。用法：尋找交叉和背離作為趨勢變化的信號。提示：在低波動性或橫盤市場中與其他指標確認。
- macds：MACD 信號線：MACD 線的 EMA 平滑。用法：使用與 MACD 線的交叉來觸發交易。提示：應作為更廣泛策略的一部分以避免誤報。
- macdh：MACD 柱狀圖：顯示 MACD 線與其信號線之間的差距。用法：可視化動能強度並及早發現背離。提示：可能不穩定；在快速變動的市場中輔以額外的過濾器。

動能指標：
- rsi：RSI：衡量動能以標記超買/超賣狀況。用法：應用 70/30 閾值並觀察背離以發出反轉信號。提示：在強勁趨勢中，RSI 可能保持極端；務必與趨勢分析交叉檢查。

波動性指標：
- boll：布林帶中軌：作為布林帶基礎的 20 SMA。用法：作為價格變動的動態基準。提示：與上下軌結合以有效發現突破或反轉。
- boll_ub：布林帶上軌：通常比中軌高 2 個標準差。用法：發出潛在超買狀況和突破區域的信號。提示：與其他工具確認信號；在強勁趨勢中價格可能會沿著軌道運行。
- boll_lb：布林帶下軌：通常比中軌低 2 個標準差。用法：指示潛在的超賣狀況。提示：使用額外分析以避免錯誤的反轉信號。
- atr：ATR：平均真實波幅，用於衡量波動性。用法：根據當前市場波動性設置止損水平和調整頭寸大小。提示：這是一個反應性指標，因此請將其用作更廣泛風險管理策略的一部分。

成交量指標：
- vwma：VWMA：按成交量加權的移動平均線。用法：通過將價格行為與成交量數據相結合來確認趨勢。提示：注意成交量激增導致的結果偏差；與其他成交量分析結合使用。

- 選擇提供多樣化和互補資訊的指標。避免冗餘（例如，不要同時選擇 rsi 和 stochrsi）。同時簡要解釋為什麼它們適合給定的市場環境。當您進行工具調用時，請使用上面提供的指標確切名稱，因為它們是已定義的參數，否則您的調用將失敗。請確保首先調用 get_stock_data 以檢索生成指標所需的 CSV。然後使用 get_indicators 與特定的指標名稱。撰寫一份關於您觀察到的趨勢的非常詳細和細緻的報告。不要只說趨勢好壞參半，請提供詳細且精細的分析和見解，以幫助交易員做出決策。"""
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
            "market_report": report,
        }

    return market_analyst_node