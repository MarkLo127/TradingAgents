# 匯入 Enum 模組，用於建立列舉類型
from enum import Enum
# 匯入 List, Optional, Dict 類型提示，用於更清晰地定義資料結構
from typing import List, Optional, Dict
# 匯入 BaseModel，用於建立資料模型
from pydantic import BaseModel


# 定義分析師類型的列舉
class AnalystType(str, Enum):
    """
    AnalystType 是一個列舉 (Enum)，定義了不同類型的分析師。
    這有助於標準化和限制分析師的角色，確保程式碼的一致性和可讀性。

    屬性:
        MARKET (str): 市場分析師，專注於市場趨勢和價格行為。
        SOCIAL (str): 社交媒體分析師，監控和分析社交媒體上的情緒和討論。
        NEWS (str): 新聞分析師，分析新聞事件對市場的影響。
        FUNDAMENTALS (str): 基本面分析師，研究公司的財務狀況和健康狀況。
    """
    MARKET = "market"  # 市場分析師
    SOCIAL = "social"  # 社交媒體分析師
    NEWS = "news"  # 新聞分析師
    FUNDAMENTALS = "fundamentals"  # 基本面分析師