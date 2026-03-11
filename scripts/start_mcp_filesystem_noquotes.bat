@echo off
setlocal

set "LOG_FILE=%~dp0mcp_noquotes.log"
> "%LOG_FILE%" (
  echo ===== MCP Start No Quotes (fixed) =====
  echo Time: %date% %time%
  echo Raw arg: %~1
)

REM npx 路径（如果已经在 PATH，可直接用 npx）
set "NPX_PATH=E:\nodejs\npx.cmd"

REM 参数检查 —— 错误信息走 stderr，避免污染 stdout
if "%~1"=="" (
  1>&2 echo ERROR: Please provide a directory path
  >> "%LOG_FILE%" echo ERROR: No directory provided
  exit /b 1
)

REM 把可能的正斜杠转换成反斜杠（可选）
set "ARG=%~1"
set "ARG=%ARG:/=\%"

>> "%LOG_FILE%" echo Using npx: "%NPX_PATH%"
>> "%LOG_FILE%" echo Final dir: "%ARG%"
>> "%LOG_FILE%" echo Exec: "%NPX_PATH%" -q -y @modelcontextprotocol/server-filesystem -- "%ARG%"
>> "%LOG_FILE%" echo ==========================

REM 关键：不要重定向 stdout；仅把 stderr 记到日志
"%NPX_PATH%" -q -y @modelcontextprotocol/server-filesystem -- "%ARG%" 2>> "%LOG_FILE%"

endlocal
