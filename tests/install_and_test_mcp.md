# 尝试全局安装 MCP Filesystem Server

## 步骤 1: 全局安装

在终端运行：
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

## 步骤 2: 查找安装位置

```bash
npm list -g @modelcontextprotocol/server-filesystem
```

或查找可执行文件：
```bash
where mcp-server-filesystem
```

## 步骤 3: 直接运行测试

找到安装路径后（例如 `E:\nodejs\node_modules\@modelcontextprotocol\server-filesystem\dist\index.js`），在终端测试：

```bash
node E:\nodejs\node_modules\@modelcontextprotocol\server-filesystem\dist\index.js F:/Python/agent_Project2
```

如果这个命令在终端成功运行，我们就可以在 Python 中使用：

```python
StdioServerParameters(
    command="node",
    args=["E:\\nodejs\\node_modules\\@modelcontextprotocol\\server-filesystem\\dist\\index.js", "F:/Python/agent_Project2"],
    env={}
)
```

## 步骤 4: 运行测试

如果找到了安装路径，创建 `tests/test_mcp_node_direct.py` 来测试。

---

**为什么这样可能有效？**

绕过 npx，直接使用 node 运行 MCP server 的 JavaScript 文件。这样可以：
1. 避免 npx 的复杂性
2. 直接控制参数传递
3. 更简单、更可靠


