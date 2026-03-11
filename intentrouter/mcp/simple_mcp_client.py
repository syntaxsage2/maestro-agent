"""
简单的 MCP 客户端实现
绕过 MCP SDK 的问题，直接使用 JSON-RPC 通信
"""
import subprocess
import json
import asyncio
from typing import Dict, Any, List, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, create_model, Field


class SimpleMCPClient:
    """简单的 MCP 客户端，直接使用 JSON-RPC 通信"""

    def __init__(self, server_name: str, command: str, args: List[str]):
        """
        Args:
            server_name: Server 名称
            command: 启动命令
            args: 命令参数
        """
        self.server_name = server_name
        self.command = command
        self.args = args
        self.proc: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.tools: List[StructuredTool] = []

    async def connect(self, timeout: int = 30):
        """连接到 MCP Server"""
        try:
            print(f"? 连接到 {self.server_name} server...")

            # 启动 server 进程
            self.proc = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 等待 server 启动
            await asyncio.sleep(1)

            # 初始化连接
            init_response = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    }
                },
                "clientInfo": {
                    "name": "intentrouter",
                    "version": "1.0.0"
                }
            }, timeout=timeout)

            if "result" not in init_response:
                raise Exception(f"初始化失败: {init_response}")

            server_info = init_response["result"].get("serverInfo", {})
            print(f"? 连接成功: {server_info.get('name')} v{server_info.get('version')}")

            # 加载工具
            await self._load_tools()

        except Exception as e:
            print(f"? 连接失败 {self.server_name}: {e}")
            if self.proc:
                self.proc.terminate()
                self.proc = None
            raise

    async def _send_request(self, method: str, params: Dict[str, Any] = None, timeout: int = 10) -> Dict:
        """发送 JSON-RPC 请求"""
        if not self.proc or self.proc.poll() is not None:
            raise Exception("Server 未运行")

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        # 发送请求
        request_str = json.dumps(request) + "\n"
        self.proc.stdin.write(request_str)
        self.proc.stdin.flush()

        # 读取响应（带超时）
        async def read_response():
            return self.proc.stdout.readline()

        try:
            response_str = await asyncio.wait_for(read_response(), timeout=timeout)
            if not response_str:
                raise Exception("Server 无响应")
            return json.loads(response_str)
        except asyncio.TimeoutError:
            raise Exception(f"请求超时: {method}")

    async def _load_tools(self):
        """从 Server 加载工具列表"""
        try:
            response = await self._send_request("tools/list", {})

            if "result" not in response:
                raise Exception(f"获取工具列表失败: {response}")

            mcp_tools = response["result"].get("tools", [])

            # 转换为 LangChain Tools
            for mcp_tool in mcp_tools:
                langchain_tool = self._convert_to_langchain_tool(mcp_tool)
                self.tools.append(langchain_tool)

            print(f"? 加载了 {len(self.tools)} 个工具")

        except Exception as e:
            print(f"?? 加载工具失败: {e}")

    def _convert_to_langchain_tool(self, mcp_tool: Dict) -> StructuredTool:
        """转换 MCP 工具为 LangChain Tool"""

        tool_name = mcp_tool.get("name", "unknown")
        tool_description = mcp_tool.get("description", "No description")

        # 创建参数模型
        input_schema = mcp_tool.get("inputSchema", {})
        args_model = self._create_args_model(tool_name, input_schema)

        # 创建异步执行函数
        async def execute_async(**kwargs) -> str:
            try:
                # 调用 MCP Server
                response = await self._send_request("tools/call", {
                    "name": tool_name,
                    "arguments": kwargs
                })

                if "result" not in response:
                    return f"执行失败: {response.get('error', 'Unknown error')}"

                # 提取结果
                result = response["result"]
                if isinstance(result, dict) and "content" in result:
                    # MCP 返回的是 content 列表
                    contents = result["content"]
                    if isinstance(contents, list):
                        texts = []
                        for item in contents:
                            if isinstance(item, dict) and "text" in item:
                                texts.append(item["text"])
                        return "\n".join(texts) if texts else str(result)
                return str(result)

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
            name=f"mcp_{self.server_name}_{tool_name}",
            description=tool_description,
            args_schema=args_model,
            func=execute_sync,  # 🔧 添加同步函数
            coroutine=execute_async,  # 🔧 保留异步函数
            metadata={
                "source": "MCP",
                "server": self.server_name,
                "original_name": tool_name,
            }
        )

    def _create_args_model(self, tool_name: str, input_schema: Dict) -> type[BaseModel]:
        """从 JSON Schema 创建 Pydantic 模型"""
        properties = input_schema.get('properties', {}) if isinstance(input_schema, dict) else {}
        required = input_schema.get('required', []) if isinstance(input_schema, dict) else []

        if not properties:
            # 没有参数，创建空模型
            return create_model(f"{tool_name}Args")

        # 构建字段
        fields = {}
        for prop_name, prop_def in properties.items():
            prop_type = str  # 简化：都用 str
            description = prop_def.get('description', '') if isinstance(prop_def, dict) else ""
            default = ... if prop_name in required else None

            fields[prop_name] = (prop_type, Field(default=default, description=description))

        return create_model(f"{tool_name}Args", **fields)

    async def disconnect(self):
        """断开连接"""
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except:
                self.proc.kill()
            self.proc = None

    def get_tools(self) -> List[StructuredTool]:
        """获取所有工具"""
        return self.tools

