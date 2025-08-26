@echo off
chcp 65001 >nul
echo 🧹 清理Git仓库中的不需要文件...
echo.

echo ⚠️  这个脚本将从Git仓库中移除以下类型的文件:
echo   - node_modules/ (Node.js依赖)
echo   - __pycache__/ (Python缓存)
echo   - .env (环境变量文件)
echo   - uploads/ (上传文件目录)
echo   - logs/ (日志文件)
echo   - *.log (日志文件)
echo.

set /p confirm="确定要继续吗? (y/N): "
if /i not "%confirm%"=="y" (
    echo 操作已取消
    pause
    exit /b 0
)

echo.
echo 📦 从Git中移除node_modules...
git rm -r --cached node_modules/ 2>nul
if exist node_modules git rm -r --cached node_modules/ 2>nul

echo 🐍 从Git中移除Python缓存...
git rm -r --cached __pycache__/ 2>nul
git rm -r --cached python_service/__pycache__/ 2>nul
git rm -r --cached python_service/venv/ 2>nul

echo 📁 从Git中移除临时目录...
git rm -r --cached uploads/ 2>nul
git rm -r --cached logs/ 2>nul
git rm -r --cached temp/ 2>nul
git rm -r --cached tmp/ 2>nul

echo 🔐 从Git中移除环境变量文件...
git rm --cached .env 2>nul

echo 📄 从Git中移除日志文件...
for %%f in (*.log) do git rm --cached "%%f" 2>nul

echo 🗂️  从Git中移除锁文件...
git rm --cached package-lock.json 2>nul
git rm --cached yarn.lock 2>nul
git rm --cached Pipfile.lock 2>nul

echo.
echo ✅ 清理完成！现在可以提交更改:
echo.
echo 💡 建议执行以下命令:
echo   git add .gitignore
echo   git commit -m "添加.gitignore文件，清理不需要的文件"
echo   git push
echo.
pause 