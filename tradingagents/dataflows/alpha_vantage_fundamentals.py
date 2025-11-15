from .alpha_vantage_common import _make_api_request


def get_fundamentals(ticker: str, curr_date: str = None) -> str:
    """
    使用 Alpha Vantage 檢索給定股票代碼的綜合基本面數據。

    Args:
        ticker (str): 公司的股票代碼
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd (Alpha Vantage 未使用)

    Returns:
        str: 公司概覽數據，包括財務比率和關鍵指標
    """
    params = {
        "symbol": ticker,
    }

    return _make_api_request("OVERVIEW", params)


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    使用 Alpha Vantage 檢索給定股票代碼的資產負債表數據。

    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度) - Alpha Vantage 未使用
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd (Alpha Vantage 未使用)

    Returns:
        str: 具有標準化欄位的資產負債表數據
    """
    params = {
        "symbol": ticker,
    }

    return _make_api_request("BALANCE_SHEET", params)


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    使用 Alpha Vantage 檢索給定股票代碼的現金流量表數據。

    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度) - Alpha Vantage 未使用
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd (Alpha Vantage 未使用)

    Returns:
        str: 具有標準化欄位的現金流量表數據
    """
    params = {
        "symbol": ticker,
    }

    return _make_api_request("CASH_FLOW", params)


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None) -> str:
    """
    使用 Alpha Vantage 檢索給定股票代碼的損益表數據。

    Args:
        ticker (str): 公司的股票代碼
        freq (str): 報告頻率：年度/季度 (預設為季度) - Alpha Vantage 未使用
        curr_date (str): 您正在交易的當前日期，格式為 yyyy-mm-dd (Alpha Vantage 未使用)

    Returns:
        str: 具有標準化欄位的損益表數據
    """
    params = {
        "symbol": ticker,
    }

    return _make_api_request("INCOME_STATEMENT", params)