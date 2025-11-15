from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .googlenews_utils import getNewsData


def get_google_news(
    query: Annotated[str, "用於搜索的查詢"],
    curr_date: Annotated[str, "當前日期，格式為 yyyy-mm-dd"],
    look_back_days: Annotated[int, "回溯天數"],
) -> str:
    """
    使用 Google News 檢索新聞文章。

    Args:
        query (str): 用於搜索的查詢。
        curr_date (str): 當前日期，格式為 yyyy-mm-dd。
        look_back_days (int): 回溯天數。

    Returns:
        str: 包含新聞報導的格式化字串。
    """
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (來源: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google 新聞，從 {before} 到 {curr_date}：\n\n{news_str}"