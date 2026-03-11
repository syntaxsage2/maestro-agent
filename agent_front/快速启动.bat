@echo off
chcp 65001 > nul
echo ========================================
echo   IntentRouter Chat 前端启动脚本
echo ========================================
echo.

REM 检查 Node.js 是否安装
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js
    echo 下载地址：https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] Node.js 版本：
node --version
echo.

REM 检查是否已安装依赖
if not exist "node_modules" (
    echo [信息] 检测到未安装依赖，开始安装...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo.
    echo [成功] 依赖安装完成
    echo.
)

REM 检查后端服务
echo [信息] 检查后端服务...
curl -s http://localhost:8000/health >nul 2>nul
if %errorlevel% neq 0 (
    echo [警告] 无法连接到后端服务 (http://localhost:8000)
    echo [提示] 请先启动 FastAPI 后端服务
    echo.
    echo 是否继续启动前端？(Y/N)
    set /p continue=
    if /i not "%continue%"=="Y" (
        echo 已取消启动
        pause
        exit /b 0
    )
) else (
    echo [成功] 后端服务运行正常
)

echo.
echo [信息] 启动前端开发服务器...
echo [提示] 服务器将运行在 http://localhost:5173
echo [提示] 按 Ctrl+C 停止服务器
echo.
echo ========================================
echo.

REM 启动开发服务器
call npm run dev

pause

