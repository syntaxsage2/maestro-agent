@echo off
REM MCP Filesystem Server 启动脚本
REM 使用方法: start_mcp_filesystem.bat <directory_path>

REM 设置 npx 路径
SET NPX_PATH=E:\nodejs\npx.cmd

REM 检查是否提供了目录参数
IF "%~1"=="" (
    echo Error: Please provide a directory path
    exit /b 1
)

REM 启动 MCP filesystem server
"%NPX_PATH%" -y @modelcontextprotocol/server-filesystem "%~1"

