from .alpha_vantage_common import _make_api_request
import json


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

    response = _make_api_request("OVERVIEW", params)
    
    # 總結基本面數據以減少 token 使用量
    try:
        data = json.loads(response) if isinstance(response, str) else response
        
        if isinstance(data, dict) and "Symbol" in data:
            # 只保留關鍵的基本面指標
            summarized_data = {
                # 基本資訊
                "Symbol": data.get("Symbol", ""),
                "Name": data.get("Name", ""),
                "Description": data.get("Description", "")[:300] if data.get("Description") else "",  # 限制描述長度
                "Sector": data.get("Sector", ""),
                "Industry": data.get("Industry", ""),
                "MarketCapitalization": data.get("MarketCapitalization", ""),
                
                # 關鍵財務指標
                "EBITDA": data.get("EBITDA", ""),
                "PERatio": data.get("PERatio", ""),
                "PEGRatio": data.get("PEGRatio", ""),
                "BookValue": data.get("BookValue", ""),
                "DividendPerShare": data.get("DividendPerShare", ""),
                "DividendYield": data.get("DividendYield", ""),
                "EPS": data.get("EPS", ""),
                "RevenuePerShareTTM": data.get("RevenuePerShareTTM", ""),
                "ProfitMargin": data.get("ProfitMargin", ""),
                "OperatingMarginTTM": data.get("OperatingMarginTTM", ""),
                "ReturnOnAssetsTTM": data.get("ReturnOnAssetsTTM", ""),
                "ReturnOnEquityTTM": data.get("ReturnOnEquityTTM", ""),
                "RevenueTTM": data.get("RevenueTTM", ""),
                "GrossProfitTTM": data.get("GrossProfitTTM", ""),
                
                # 交易指標
                "52WeekHigh": data.get("52WeekHigh", ""),
                "52WeekLow": data.get("52WeekLow", ""),
                "50DayMovingAverage": data.get("50DayMovingAverage", ""),
                "200DayMovingAverage": data.get("200DayMovingAverage", ""),
                
                # 財務健康指標
                "QuarterlyEarningsGrowthYOY": data.get("QuarterlyEarningsGrowthYOY", ""),
                "QuarterlyRevenueGrowthYOY": data.get("QuarterlyRevenueGrowthYOY", ""),
                "AnalystTargetPrice": data.get("AnalystTargetPrice", ""),
                "Beta": data.get("Beta", ""),
            }
            
            return json.dumps(summarized_data, ensure_ascii=False, indent=2)
        
        return response
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"警告：無法總結基本面數據：{e}")
        return response


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

    response = _make_api_request("BALANCE_SHEET", params)
    
    # 限制返回的報告數量以減少 token 使用量
    try:
        data = json.loads(response) if isinstance(response, str) else response
        
        if isinstance(data, dict):
            # 只保留最近的 2 份報告（而不是全部歷史）
            if "quarterlyReports" in data and isinstance(data["quarterlyReports"], list):
                data["quarterlyReports"] = data["quarterlyReports"][:2]
            if "annualReports" in data and isinstance(data["annualReports"], list):
                data["annualReports"] = data["annualReports"][:2]
            
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return response
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"警告：無法處理資產負債表數據：{e}")
        return response


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

    response = _make_api_request("CASH_FLOW", params)
    
    # 限制返回的報告數量以減少 token 使用量
    try:
        data = json.loads(response) if isinstance(response, str) else response
        
        if isinstance(data, dict):
            # 只保留最近的 2 份報告（而不是全部歷史）
            if "quarterlyReports" in data and isinstance(data["quarterlyReports"], list):
                data["quarterlyReports"] = data["quarterlyReports"][:2]
            if "annualReports" in data and isinstance(data["annualReports"], list):
                data["annualReports"] = data["annualReports"][:2]
            
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return response
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"警告：無法處理現金流量表數據：{e}")
        return response


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

    response = _make_api_request("INCOME_STATEMENT", params)
    
    # 限制返回的報告數量以減少 token 使用量
    try:
        data = json.loads(response) if isinstance(response, str) else response
        
        if isinstance(data, dict):
            # 只保留最近的 2 份報告（而不是全部歷史）
            if "quarterlyReports" in data and isinstance(data["quarterlyReports"], list):
                data["quarterlyReports"] = data["quarterlyReports"][:2]
            if "annualReports" in data and isinstance(data["annualReports"], list):
                data["annualReports"] = data["annualReports"][:2]
            
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return response
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"警告：無法處理損益表數據：{e}")
        return response