@echo off
chcp 65001 > nul
title TradingView Auto Download

echo.
echo ============================================================
echo   TradingView Chart Data Auto Download
echo ============================================================
echo.
echo This script will:
echo   - Close Chrome
echo   - Run Python script
echo   - Download 38 tickers (5-10 minutes)
echo.
pause

echo.
echo [1/2] Closing Chrome...
echo ============================================================
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1
timeout /t 1 /nobreak >nul
echo Done.
echo.

echo [2/2] Starting download...
echo ============================================================
echo.

python tv_export.py

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo ERROR occurred
    echo ============================================================
    echo.
    echo Check debug.log file.
    echo.
    echo Solution:
    echo   1. Close all chrome.exe in Task Manager
    echo   2. Run START_HERE.bat again
    echo.
) else (
    echo.
    echo ============================================================
    echo COMPLETED!
    echo ============================================================
    echo.
    echo CSV files saved in exports folder
    echo.
)

pause
