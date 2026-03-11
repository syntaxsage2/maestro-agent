@echo off
REM MCP Filesystem Server 调试启动脚本

REM 记录日志到文件
SET LOG_FILE=%~dp0mcp_debug.log

echo ===== MCP Start Debug ===== > "%LOG_FILE%"
echo Time: %date% %time% >> "%LOG_FILE%"
echo Arguments count: %0 >> "%LOG_FILE%"
echo Arg 0: %0 >> "%LOG_FILE%"
echo Arg 1: %1 >> "%LOG_FILE%"
echo Arg 2: %2 >> "%LOG_FILE%"
echo Full command: %* >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

REM 设置 npx 路径
SET NPX_PATH=E:\nodejs\npx.cmd

REM 检查参数
IF "%~1"=="" (
    echo ERROR: No directory provided >> "%LOG_FILE%"
    echo Error: Please provide a directory path
    exit /b 1
)

echo NPX Path: %NPX_PATH% >> "%LOG_FILE%"
echo Directory: %~1 >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"
echo Executing: "%NPX_PATH%" -y @modelcontextprotocol/server-filesystem "%~1" >> "%LOG_FILE%"
echo ========================== >> "%LOG_FILE%"

REM 启动 MCP filesystem server（将错误也记录）
"%NPX_PATH%" -y @modelcontextprotocol/server-filesystem "%~1" 2>> "%LOG_FILE%"

