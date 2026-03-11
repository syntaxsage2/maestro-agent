"""
时间工具
"""
import zoneinfo
from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time(timezone: str = "Asia/Shanghai", format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前日期和实践

    Args:
        timezone: 时区名称,例如 "Asia/Shanghai", UTC
        fomat: 时间格式

    Returns:
        str: 格式化实践字符串
    """
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("Asia/Shanghai")

    now = datetime.now(tz)
    return now.strftime(format)