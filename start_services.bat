@echo off
chcp 65001 >nul
echo 🚀 启动数学文档处理系统...
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker未安装或未启动，请先安装并启动Docker
    echo 📥 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 创建必要目录
echo 📁 创建必要目录...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "chroma_config" mkdir chroma_config

REM 启动ChromaDB
echo 🗄️  启动ChromaDB向量数据库...
docker run -d --name math-doc-chromadb -p 8000:8000 chromadb/chroma:latest
if %errorlevel% neq 0 (
    echo ⚠️  ChromaDB容器可能已存在，尝试启动现有容器...
    docker start math-doc-chromadb
)

REM 等待ChromaDB启动
echo ⏳ 等待ChromaDB启动...
timeout /t 10 /nobreak >nul

echo ✅ 服务启动完成！
echo.
echo 🌐 访问地址:
echo   - 主服务API: http://localhost:3000
echo   - Python解析服务: http://localhost:8001  
echo   - ChromaDB: http://localhost:8000
echo.
echo 📝 接下来请手动启动:
echo   1. Python服务: 在新的命令行窗口运行 start_python.bat
echo   2. Node.js服务: 在新的命令行窗口运行 start_nodejs.bat
echo.
pause 