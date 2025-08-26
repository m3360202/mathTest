@echo off
chcp 65001 >nul
echo 🐍 启动Python文档解析微服务...
echo.

REM 检查Python是否安装
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装，请先安装Python 3.11+
    pause
    exit /b 1
)

REM 进入Python服务目录
cd python_service

REM 检查依赖是否安装
py -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 安装Python依赖...
    py -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 启动FastAPI服务
echo ✅ 启动Python服务在端口8001...
echo 🌐 访问 http://localhost:8001/docs 查看API文档
echo 🛑 按Ctrl+C停止服务
echo.
py -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload 