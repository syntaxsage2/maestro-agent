"""
搜索工具
"""

from langchain_core.tools import tool

@tool
def web_search(query: str, max_results: int=5) -> list[dict]:
    """
    在互联网上 搜索信息,用于查找最新资讯,实时数据等需要联网的信息

    Args:
        query: 搜索关键词
        max_results: 返回结果数量，默认 5 条

    Returns:
        list[dict]: 搜索结果列表，每个结果包含 title, snippet, url
    """
    try:
        from ddgs import DDGS
    except ImportError:
        raise ImportError("请安装 duckduckgo-search: pip install duckduckgo-search")

    try:
        with DDGS() as ddgs:
            result = []
            for r in ddgs.text(query, max_results=max_results):
                result.append({
                    "title": r.get('title', ""),
                    "snippet": r.get('body', ""),
                    "url": r.get('href', ""),
                })
            return result
    except Exception as e:
        raise RuntimeError(f"搜索失败: {str(e)}")