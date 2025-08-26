@echo off
chcp 65001 >nul
echo 🛑 停止数学文档处理系统...
echo.

REM 停止ChromaDB容器
echo 📦 停止ChromaDB容器...
docker stop math-doc-chromadb >nul 2>&1
docker rm math-doc-chromadb >nul 2>&1

REM 提示手动停止其他服务
echo ⚠️  请手动停止以下服务:
echo   - Python服务: 在Python服务窗口按Ctrl+C
echo   - Node.js服务: 在Node.js服务窗口按Ctrl+C
echo.
echo ✅ ChromaDB已停止
pause 