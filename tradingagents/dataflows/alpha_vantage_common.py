import os
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO

API_BASE_URL = "https://www.alphavantage.co/query"

def get_api_key() -> str:
    """從環境變數中檢索 Alpha Vantage 的 API 金鑰。"""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("未設定 ALPHA_VANTAGE_API_KEY 環境變數。")
    return api_key

def format_datetime_for_api(date_input) -> str:
    """將各種日期格式轉換為 Alpha Vantage API 所需的 YYYYMMDDTHHMM 格式。"""
    if isinstance(date_input, str):
        # 如果已經是正確格式，則直接返回
        if len(date_input) == 13 and 'T' in date_input:
            return date_input
        # 嘗試解析常見的日期格式
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y%m%dT0000")
        except ValueError:
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y%m%dT%H%M")
            except ValueError:
                raise ValueError(f"不支援的日期格式：{date_input}")
    elif isinstance(date_input, datetime):
        return date_input.strftime("%Y%m%dT%H%M")
    else:
        raise ValueError(f"日期必須是字串或日期時間物件，但得到的是 {type(date_input)}")

class AlphaVantageRateLimitError(Exception):
    """當超過 Alpha Vantage API 速率限制時引發的例外。"""
    pass

def _make_api_request(function_name: str, params: dict) -> dict | str:
    """
    發送 API 請求並處理回應的輔助函式。
    
    Raises:
        AlphaVantageRateLimitError: 當超過 API 速率限制時
    """
    # 建立 params 的副本以避免修改原始字典
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # 如果 params 或全域變數中存在，則處理 entitlement 參數
    current_entitlement = globals().get('_current_entitlement')
    entitlement = api_params.get("entitlement") or current_entitlement
    
    if entitlement:
        api_params["entitlement"] = entitlement
    elif "entitlement" in api_params:
        # 如果 entitlement 為 None 或空，則移除
        api_params.pop("entitlement", None)
    
    response = requests.get(API_BASE_URL, params=api_params)
    response.raise_for_status()

    response_text = response.text
    
    # 檢查回應是否為 JSON (錯誤回應通常是 JSON)
    try:
        response_json = json.loads(response_text)
        # 檢查速率限制錯誤
        if "Information" in response_json:
            info_message = response_json["Information"]
            if "rate limit" in info_message.lower() or "api key" in info_message.lower():
                raise AlphaVantageRateLimitError(f"超過 Alpha Vantage 速率限制：{info_message}")
    except json.JSONDecodeError:
        # 回應不是 JSON (可能是 CSV 數據)，這是正常的
        pass

    return response_text



def _filter_csv_by_date_range(csv_data: str, start_date: str, end_date: str) -> str:
    """
    過濾 CSV 數據，只包含指定日期範圍內的資料列。

    Args:
        csv_data: 來自 Alpha Vantage API 的 CSV 字串
        start_date: 開始日期，格式為 yyyy-mm-dd
        end_date: 結束日期，格式為 yyyy-mm-dd

    Returns:
        過濾後的 CSV 字串
    """
    if not csv_data or csv_data.strip() == "":
        return csv_data

    try:
        # 解析 CSV 數據
        df = pd.read_csv(StringIO(csv_data))

        # 假設第一欄是日期欄 (時間戳)
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])

        # 按日期範圍過濾
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        filtered_df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]

        # 轉換回 CSV 字串
        return filtered_df.to_csv(index=False)

    except Exception as e:
        # 如果過濾失敗，返回原始數據並附帶警告
        print(f"警告：按日期範圍過濾 CSV 數據失敗：{e}")
        return csv_data