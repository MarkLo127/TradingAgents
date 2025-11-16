# 匯入 questionary 套件，用於建立互動式命令列提示
import questionary
# 匯入類型提示，用於更清晰地定義函式簽名
from typing import List, Optional, Tuple, Dict

# 從 cli.models 模組匯入 AnalystType 列舉
from cli.models import AnalystType

# 定義分析師的順序和對應的類型
ANALYST_ORDER = [
    ("市場分析師", AnalystType.MARKET),
    ("社群媒體分析師", AnalystType.SOCIAL),
    ("新聞分析師", AnalystType.NEWS),
    ("基本面分析師", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """
    提示使用者輸入股票代碼。

    返回:
        str: 使用者輸入的股票代碼，已轉換為大寫並去除頭尾空格。
    """
    ticker = questionary.text(
        "請輸入要分析的股票代碼：",
        # 驗證輸入是否為空
        validate=lambda x: len(x.strip()) > 0 or "請輸入有效的股票代碼。",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有輸入，則退出程式
    if not ticker:
        console.print("\n[red]未提供股票代碼。正在結束程式...[/red]")
        exit(1)

    # 返回處理過的股票代碼
    return ticker.strip().upper()


def get_analysis_date() -> str:
    """
    提示使用者輸入 YYYY-MM-DD 格式的日期。

    返回:
        str: 使用者輸入的日期字串。
    """
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        """驗證日期字串是否為 YYYY-MM-DD 格式"""
        # 使用正規表示式檢查格式
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            # 嘗試將字串解析為日期物件
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "請輸入分析日期 (YYYY-MM-DD)：",
        # 驗證日期格式是否正確
        validate=lambda x: validate_date(x.strip())
        or "請輸入有效的 YYYY-MM-DD 格式日期。",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有輸入，則退出程式
    if not date:
        console.print("\n[red]未提供日期。正在結束程式...[/red]")
        exit(1)

    # 返回處理過的日期字串
    return date.strip()


def select_analysts() -> List[AnalystType]:
    """
    使用互動式核取方塊選擇分析師。

    返回:
        List[AnalystType]: 使用者選擇的分析師類型列表。
    """
    choices = questionary.checkbox(
        "選擇您的 [分析師團隊]：",
        # 設定可選項
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        # 提供操作說明
        instruction="\n- 按下空白鍵選擇/取消選擇分析師\n- 按下 'a' 鍵選擇/取消選擇所有\n- 完成後按下 Enter 鍵",
        # 驗證至少選擇一位分析師
        validate=lambda x: len(x) > 0 or "您必須至少選擇一位分析師。",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有選擇，則退出程式
    if not choices:
        console.print("\n[red]未選擇任何分析師。正在結束程式...[/red]")
        exit(1)

    # 返回選擇的分析師列表
    return choices


def select_research_depth() -> int:
    """
    使用互動式選單選擇研究深度。

    返回:
        int: 代表研究深度的整數。
    """

    # 定義研究深度的選項及其對應值
    DEPTH_OPTIONS = [
        ("淺層 - 快速研究，較少的辯論和策略討論", 1),
        ("中等 - 中等程度，適度的辯論和策略討論", 3),
        ("深層 - 全面研究，深入的辯論和策略討論", 5),
    ]

    choice = questionary.select(
        "選擇您的 [研究深度]：",
        # 設定可選項
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        # 提供操作說明
        instruction="\n- 使用方向鍵導覽\n- 按下 Enter 鍵選擇",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有選擇，則退出程式
    if choice is None:
        console.print("\n[red]未選擇研究深度。正在結束程式...[/red]")
        exit(1)

    # 返回選擇的研究深度
    return choice


def select_shallow_thinking_agent(provider) -> str:
    """
    使用互動式選單選擇淺層思維的 LLM 引擎。

    參數:
        provider (str): LLM 供應商的名稱。

    返回:
        str: 選擇的 LLM 模型的名稱。
    """

    # 定義不同供應商的淺層思維 LLM 引擎選項
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-5.1", "gpt-5.1-2025-11-13"),
            ("GPT-5-mini","gpt-5-mini-2025-08-07"),
            ("GPT-5-nano","gpt-5-nano-2025-08-07"),
            ("GPT-4.1-mini", "gpt-4.1-mini"),
            ("GPT-4.1-nano", "gpt-4.1-nano"),
            ("GPT-4o", "gpt-4o"),
            ("GPT-4o-mini", "gpt-4o-mini")
        ],
        "anthropic": [
            ("Claude Haiku 3.5", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash", "gemini-2.5-flash-preview-05-20"),
        ],
        "openrouter": [
            ("Meta: Llama 4 Scout", "meta-llama/llama-4-scout:free"),
            ("Meta: Llama 3.3 8B Instruct - Llama 3.3 70B", "meta-llama/llama-3.3-8b-instruct:free"),
            ("google/gemini-2.0-flash-exp:free - Gemini Flash 2.0", "google/gemini-2.0-flash-exp:free"),
        ],
        "ollama": [
            ("llama3.1 本機版", "llama3.1"),
            ("llama3.2 本機版", "llama3.2"),
        ]
    }

    choice = questionary.select(
        "選擇您的 [快速思維 LLM 引擎]：",
        # 根據供應商顯示選項
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS[provider.lower()]
        ],
        # 提供操作說明
        instruction="\n- 使用方向鍵導覽\n- 按下 Enter 鍵選擇",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有選擇，則退出程式
    if choice is None:
        console.print(
            "\n[red]未選擇快速思維 LLM 引擎。正在結束程式...[/red]"
        )
        exit(1)

    # 返回選擇的 LLM 模型
    return choice


def select_deep_thinking_agent(provider) -> str:
    """
    使用互動式選單選擇深層思維的 LLM 引擎。

    參數:
        provider (str): LLM 供應商的名稱。

    返回:
        str: 選擇的 LLM 模型的名稱。
    """

    # 定義不同供應商的深層思維 LLM 引擎選項
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("GPT-5.1", "gpt-5.1-2025-11-13"),
            ("GPT-5-mini","gpt-5-mini-2025-08-07"),
            ("GPT-5-nano","gpt-5-nano-2025-08-07"),
            ("GPT-4.1-mini", "gpt-4.1-mini"),
            ("GPT-4.1-nano", "gpt-4.1-nano"),
            ("GPT-4o", "gpt-4o"),
            ("GPT-4o-mini", "gpt-4o-mini")
        ],
        "anthropic": [
            ("Claude Haiku 3.5", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4", "claude-sonnet-4-0"),
            ("Claude Opus 4", "claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro", "gemini-2.5-pro-preview-06-05"),
        ],
        "openrouter": [
            ("DeepSeek V3 - 一個 685B 參數的專家混合模型", "deepseek/deepseek-chat-v3-0324:free"),
            ("Deepseek - DeepSeek 團隊旗艦聊天模型的最新版本", "deepseek/deepseek-chat-v3-0324:free"),
        ],
        "ollama": [
            ("llama3.1 本機版", "llama3.1"),
            ("qwen3", "qwen3"),
        ]
    }
    
    choice = questionary.select(
        "選擇您的 [深度思維 LLM 引擎]：",
        # 根據供應商顯示選項
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS[provider.lower()]
        ],
        # 提供操作說明
        instruction="\n- 使用方向鍵導覽\n- 按下 Enter 鍵選擇",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    # 如果使用者沒有選擇，則退出程式
    if choice is None:
        console.print("\n[red]未選擇深度思維 LLM 引擎。正在結束程式...[/red]")
        exit(1)

    # 返回選擇的 LLM 模型
    return choice

def select_llm_provider() -> tuple[str, str]:
    """
    使用互動式選單選擇 LLM 供應商。

    返回:
        tuple[str, str]: 包含供應商顯示名稱和 API 基礎 URL 的元組。
    """
    # 定義 LLM 供應商及其 API 基礎 URL
    BASE_URLS = [
        ("OpenAI", "https://api.openai.com/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),        
    ]
    
    choice = questionary.select(
        "選擇您的 LLM 供應商：",
        # 設定可選項
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        # 提供操作說明
        instruction="\n- 使用方向鍵導覽\n- 按下 Enter 鍵選擇",
        # 設定提示的樣式
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    # 如果使用者沒有選擇，則退出程式
    if choice is None:
        console.print("\n[red]未選擇 LLM 後端。正在結束程式...[/red]")
        exit(1)
    
    # 解構選擇的元組
    display_name, url = choice
    # 印出使用者的選擇
    print(f"您選擇了：{display_name}\tURL: {url}")
    
    # 返回供應商名稱和 URL
    return display_name, url