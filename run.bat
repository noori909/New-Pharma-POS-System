@echo off
title New Quetta Surgical and Medicine Distribution - POS
cd /d "%~dp0"

echo =======================================================
echo Starting NQS POS System...
echo =======================================================

if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" main.py
) else (
    python main.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo =======================================================
    echo Application closed with an error code: %ERRORLEVEL%
    echo Please see the error message above for details.
    echo =======================================================
    pause
)
