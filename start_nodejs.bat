@echo off
chcp 65001 >nul
echo 🟢 启动Node.js主API服务...
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js 16+
    echo 📥 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查依赖是否安装
if not exist "node_modules" (
    echo 📦 安装Node.js依赖...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 启动Node.js服务
echo ✅ 启动Node.js服务在端口3000...
echo 🌐 主服务地址: http://localhost:3000
echo 🧪 健康检查: http://localhost:3000/health
echo 🛑 按Ctrl+C停止服务
echo.
node server.js 