"""
天气工具（Mock 实现）
"""
from langchain_core.tools import tool


@tool
def get_weather(city: str, unit: str = "celsius") -> dict:
    """
    获取指定城市的当前天气信息，包括温度、湿度、天气状况等。

    Args:
        city: 城市名称，例如 'Beijing', 'Shanghai', 'New York'
        unit: 温度单位，'celsius'（摄氏度）或 'fahrenheit'（华氏度）

    Returns:
        dict: 天气信息，包含 temperature, condition, humidity 等字段
    """
    # ⚠️ 这是 Mock 实现，实际应该调用天气 API
    # 例如：OpenWeatherMap, WeatherAPI.com 等

    # TODO: 实际实现
    # from intentrouter.config import settings
    # if settings.WEATHER_API_KEY:
    #     import httpx
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(...)

    # Mock 数据
    return {
        "city": city,
        "temperature": 22.5 if unit == "celsius" else 72.5,
        "condition": "晴朗",
        "humidity": "65%",
        "note": "这是模拟数据，需要配置 API Key 才能获取真实数据"
    }