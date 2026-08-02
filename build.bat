@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py

if not defined PY (
    echo 未找到 Python，请先安装 Python 3.8+ 并勾选 "Add to PATH"
    pause
    exit /b 1
)

echo [1/3] 安装依赖...
%PY% -m pip install -r requirements.txt -q
%PY% -m pip install -r requirements-build.txt -q

echo [2/3] 开始打包...
%PY% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "游戏按键辅助" ^
    --hidden-import=keyboard ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pynput.mouse ^
    --collect-all keyboard ^
    main.py

if errorlevel 1 (
    echo 打包失败
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo 可执行文件位置: dist\游戏按键辅助.exe
echo.
echo 提示：
echo   - 首次运行建议右键 exe，选择「以管理员身份运行」
echo   - 配置文件 config.json 会生成在 exe 同目录
echo.
pause
