"""
MCP 客户端 - 连接外部MCP Server
"""
import asyncio
from typing import List, Dict

from langchain_core.tools import StructuredTool
from mcp import StdioServerParameters, ClientSession, stdio_client
from pydantic import BaseModel, create_model, Field


class MCPClientWrapper:
    """MCP 客户端包装器"""
    def __init__(self, server_name: str, command: str, args: List[str], env: Dict[str, str] = None):
        """
        Args:
            server_name: Server 名称
            command: 启动命令
            args: 命令参数
            env: 环境变量
        """
        self.server_name = server_name
        self.server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env or {}
        )
        self.session: ClientSession = None
        self.tools: List[StructuredTool] = []
        self._context_manager = None
        self._read = None
        self._write = None

    async def connect(self, timeout: int = 30):
        """连接到MCP Server
        
        Args:
            timeout: 连接超时时间（秒），默认30秒
        """
        async def _do_connect():
            # 创建上下文管理器
            self._context_manager = stdio_client(self.server_params)
            
            # 进入上下文
            self._read, self._write = await self._context_manager.__aenter__()
            
            # 创建会话
            self.session = ClientSession(self._read, self._write)

            # 初始化
            await self.session.initialize()

            # 获取工具列表
            await self._load_tools()
        
        try:
            # 使用 wait_for 实现超时（兼容 Python 3.7+）
            await asyncio.wait_for(_do_connect(), timeout=timeout)
            
        except asyncio.TimeoutError:
            print(f"❌ 连接超时 {self.server_name}: 超过 {timeout} 秒")
            # 清理资源
            if self._context_manager:
                try:
                    await self._context_manager.__aexit__(None, None, None)
                except:
                    pass
            raise
        except Exception as e:
            print(f"❌ 连接失败 {self.server_name}: {e}")
            # 清理资源
            if self._context_manager:
                try:
                    await self._context_manager.__aexit__(None, None, None)
                except:
                    pass
            raise

    async def _load_tools(self):
        """从 Server 加载工具列表"""
        try:
            # 调用MCP的tools/list方法
            result = await self.session.list_tools()

            # 转换为LangChain Tools
            for mcp_tool in result.tools:
                langchain_tool = self._convert_to_langchain_tool(mcp_tool)
                self.tools.append(langchain_tool)

        except Exception as e:
            print(f"⚠️ 加载工具失败: {e}")

    def _convert_to_langchain_tool(self, mcp_tool) -> StructuredTool:
        """转换MCP工具为LangChain Tool"""

        # 创建参数模型
        input_schema = mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else {}
        args_model = self._create_args_model(mcp_tool.name, input_schema)

        # 创建异步执行函数
        async def execute_async(**kwargs) -> str:
            try:
                # 调用 MCP Server
                result = await self.session.call_tool(mcp_tool.name, kwargs)

                # 提取结果
                if hasattr(result, 'content') and result.content:
                    # MCP返回的是content 列表
                    texts = []
                    for item in result.content:
                        if hasattr(item, 'text'):
                            texts.append(item.text)
                    return "\n".join(texts) if texts else str(result)
            except Exception as e:
                return f"执行失败: {str(e)}"

        # 创建同步包装器（用于同步上下文）
        def execute_sync(**kwargs) -> str:
            """同步包装器：在同步上下文中运行异步代码"""
            try:
                # 尝试获取当前运行的 event loop
                try:
                    loop = asyncio.get_running_loop()
                    # 如果已经在异步上下文中，不能使用 asyncio.run()
                    # 这种情况下应该使用异步调用，但这里作为后备方案
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, execute_async(**kwargs))
                        return future.result(timeout=30)
                except RuntimeError:
                    # 没有运行的 event loop，可以使用 asyncio.run()
                    return asyncio.run(execute_async(**kwargs))
            except Exception as e:
                return f"执行失败: {str(e)}"

        return StructuredTool(
            name=f"mcp_{self.server_name}_{mcp_tool.name}",
            description=mcp_tool.description or "No description",
            args_schema=args_model,  # 🔧 修正参数名
            func=execute_sync,  # 🔧 添加同步函数
            coroutine=execute_async,  # 🔧 保留异步函数
            metadata={
                "source": "MCP",
                "server": self.server_name,
                "original_name": mcp_tool.name,
            }
        )

    def _create_args_model(self, tool_name: str, input_schema: Dict) -> type[BaseModel]:
        """从JSON Schema 创建 Pydantic模型"""
        properties = input_schema.get('properties', {}) if isinstance(input_schema, dict) else {}
        required = input_schema.get('required', []) if isinstance(input_schema, dict) else []

        if not properties:
            # 没有参数， 创建空模型
            return create_model(f"{tool_name}Args")

        # 构建字段
        fields = {}
        for prop_name, prop_def in properties.items():
            prop_type = str  # 简化 都用str
            description = prop_def.get('description') if isinstance(prop_def, dict) else ""
            default = ... if prop_name in required else None

            fields[prop_name] = (prop_type, Field(default=default, description=description))

        return create_model(f"{tool_name}Args",**fields)

    async def disconnect(self):
        """断开连接"""
        if self._context_manager:
            try:
                await self._context_manager.__aexit__(None, None, None)
            except Exception as e:
                print(f"⚠️ 断开连接时出错 {self.server_name}: {e}")
            finally:
                self._context_manager = None
                self._read = None
                self._write = None
                self.session = None

    def get_tools(self) -> List[StructuredTool]:
        """获取所有工具"""
        return self.tools






