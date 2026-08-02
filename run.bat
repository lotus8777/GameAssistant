@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1 && set PY=python
if not defined PY where py >nul 2>&1 && set PY=py

if not defined PY (
    echo 未找到 Python，请先安装 Python 3.8+ 并勾选 "Add to PATH"
    echo 下载: https://www.python.org/downloads/
    pause
    exit /b 1
)

%PY% -m pip install -r requirements.txt -q
%PY% main.py
pause
