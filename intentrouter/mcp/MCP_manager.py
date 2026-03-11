"""
MCP 管理器 - 管理多个MCP Server连接
"""
from typing import List, Dict

from langchain_core.tools import BaseTool

from intentrouter.mcp.simple_mcp_client import SimpleMCPClient


class MCPManager:
    def __init__(self):
        self.clients: List[SimpleMCPClient] = []
        self.all_tools: List[BaseTool] = []

    async def add_server(self, name: str, command: str, args: List[str]) -> bool:
        """
        添加并连接到 MCP Server

        Args:
            name: server 名称
            command: 启动命令
            args: 参数列表
        """
        try:
            client = SimpleMCPClient(name, command, args)
            await client.connect()

            self.clients.append(client)
            self.all_tools.extend(client.get_tools())

            print(f"✅ 成功连接到 {name} server，加载了 {len(client.get_tools())} 个工具")
            return True

        except Exception as e:
            print(f"❌ 添加 Server 失败 {name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def disconnect_all(self):
        """断开所有连接"""
        for client in self.clients:
            await client.disconnect()
        self.clients.clear()
        self.all_tools.clear()

    def get_all_tools(self) -> List[BaseTool]:
        return self.all_tools

_mcp_manager: MCPManager = None


async def get_mcp_manager():
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPManager()
        # 添加默认的 MCP Servers
        await _init_default_servers(_mcp_manager)
    return _mcp_manager


async def _init_default_servers(manager: MCPManager):
    """
    初始化默认的 MCP Servers
    
    使用直接的 node 命令运行 MCP server，绕过 npx 的问题
    """
    import os
    import sys
    import subprocess

    # 获取项目根目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    # 转换为正斜杠格式
    project_root = project_root.replace("\\", "/")
    
    print(f"📁 初始化 MCP Filesystem Server")
    print(f"📁 允许访问目录: {project_root}")

    # 查找全局安装的 MCP filesystem server
    server_path = None
    
    # 常见的 npm 全局目录位置
    potential_npm_roots = [
        r"E:\nodejs\node_global\node_modules",  # 用户的配置
        r"E:\nodejs\node_modules",
        os.path.expanduser(r"~\AppData\Roaming\npm\node_modules"),
        r"C:\Program Files\nodejs\node_modules",
    ]
    
    # 尝试查找 MCP server
    for npm_root in potential_npm_roots:
        potential_path = os.path.join(
            npm_root,
            "@modelcontextprotocol",
            "server-filesystem",
            "dist",
            "index.js"
        )
        if os.path.exists(potential_path):
            server_path = potential_path
            print(f"🔧 找到 MCP server: {server_path}")
            break
    
    # 如果没找到，尝试用 npm 命令查找
    if not server_path:
        try:
            result = subprocess.run(
                ["npm", "root", "-g"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True  # Windows 需要 shell=True
            )
            if result.returncode == 0:
                npm_root = result.stdout.strip()
                potential_path = os.path.join(
                    npm_root,
                    "@modelcontextprotocol",
                    "server-filesystem",
                    "dist",
                    "index.js"
                )
                if os.path.exists(potential_path):
                    server_path = potential_path
                    print(f"🔧 找到 MCP server: {server_path}")
        except Exception as e:
            print(f"⚠️ 使用 npm 查找时出错: {e}")
    
    if not server_path:
        print("❌ 未找到全局安装的 MCP filesystem server")
        print("💡 请运行: npm install -g @modelcontextprotocol/server-filesystem")
        return
    
    # 使用 node 直接运行 server
    command = "node"
    args = [server_path, project_root]

    print(f"🔧 参数: {args}")
    print(f"🔧 命令:这是 {command}")
    
    await manager.add_server(
        name="filesystem",
        command=command,
        args=args
    )
