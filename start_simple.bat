@echo off
chcp 65001 >nul
echo 🚀 启动数学文档处理系统（简化版）...
echo.

REM 创建必要目录
echo 📁 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs

echo ✅ 准备完成！现在请按以下步骤启动服务：
echo.
echo 📋 启动步骤：
echo   1️⃣  打开新的命令行窗口，运行: .\start_python.bat
echo   2️⃣  等待Python服务启动完成后，再打开另一个命令行窗口，运行: .\start_nodejs.bat
echo.
echo 🌐 启动完成后访问地址：
echo   - 主服务API: http://localhost:3000
echo   - Python解析服务: http://localhost:8001
echo   - 健康检查: http://localhost:3000/health
echo.
echo 🧪 测试命令：
echo   python test_client.py --health
echo.
pause 