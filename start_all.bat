@echo off
chcp 65001 >nul
echo ========================================
echo   IntentRouter Pro - 一键启动
echo ========================================
echo.

echo [1/2] 启动后端服务...
start "IntentRouter Backend" cmd /k "cd /d f:\Python\agent_Project2 && python -m uvicorn intentrouter.api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5

echo [2/2] 启动前端服务...
start "IntentRouter Frontend" cmd /k "cd /d f:\Python\agent_Project2\agent_front && npm run dev"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo   API文档: http://localhost:8000/docs
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul













