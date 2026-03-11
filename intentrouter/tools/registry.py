"""
工具注册表
"""
from typing import Optional

from langchain_core.tools import BaseTool


class ToolsRegistry:
    """工具注册表(单例模式)"""
    _instance: Optional["ToolsRegistry"] = None
    _tools: dict[str, BaseTool] = {}  # 字典 键为str， 值为BaseTool
    _mcp_loaded: bool = False  # 🆕 初始化 MCP 加载状态

    def __new__(cls):  # 重写了创建对象的方法
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self,tool: BaseTool) -> None:
        """注册工具"""
        if tool.name in self._tools:
            raise ValueError(f"工具{tool.name}已存在")
        self._tools[tool.name] = tool
        print(f"✅ 工具已注册: {tool.name}")

    def unregister(self, name: str) -> None:
        """移除工具"""
        if name in self._tools:
            del self._tools[name]
            print(f"❌ 工具已移除: {name}")

    def get(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """列出所有工具名称"""
        return list(self._tools.keys())

    def get_all_tools(self) -> list[BaseTool]:
        """获取所有工具实例"""
        return list(self._tools.values())

    def clear(self) -> None:
        """清空所有工具"""
        return self._tools.clear()

    # 🆕 MCP 相关方法

    def is_mcp_loaded(self) -> bool:
        """检查 MCP 是否已加载"""
        return self._mcp_loaded

    def mark_mcp_loaded(self):
        """标记 MCP 已加载"""
        self._mcp_loaded = True


# 全局实例
tools_registry = ToolsRegistry()