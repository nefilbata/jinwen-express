@echo off
chcp 65001 >nul
title 金文日报 - Jinwen Daily

echo ========================================
echo   金文日报 Jinwen Daily
echo   http://localhost:3000
echo ========================================
echo.

echo [1/2] 启动后端 API (port 8000)...
start "金文日报-后端" cmd /k "cd /d "%~dp0backend" && python main.py"

timeout /t 2 /nobreak >nul

echo [2/2] 启动前端界面 (port 3000)...
start "金文日报-前端" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo   启动完成！
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000/docs
echo   API:  http://localhost:8000/api/v1
echo ========================================
echo.
echo 关闭此窗口不影响服务运行。
echo 需要手动触发抓取:
echo   curl -X POST "http://localhost:8000/api/v1/admin/crawl?api_key=jinwen-admin-2026"
echo.
pause
