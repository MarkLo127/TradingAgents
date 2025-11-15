from .alpha_vantage_common import _make_api_request, format_datetime_for_api

def get_news(ticker, start_date, end_date) -> dict[str, str] | str:
    """
    返回全球主要新聞機構的即時和歷史市場新聞與情緒數據。

    涵蓋股票、加密貨幣、外匯以及財政政策、併購、IPO 等主題。

    Args:
        ticker: 新聞文章的股票代碼。
        start_date: 新聞搜索的開始日期。
        end_date: 新聞搜索的結束日期。

    Returns:
        包含新聞情緒數據的字典或 JSON 字串。
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "50",
    }
    
    return _make_api_request("NEWS_SENTIMENT", params)

def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """
    返回主要利益相關者的最新和歷史內部交易。

    涵蓋創始人、高階主管、董事會成員等的交易。

    Args:
        symbol: 股票代碼。範例："IBM"。

    Returns:
        包含內部交易數據的字典或 JSON 字串。
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)
