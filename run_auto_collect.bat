@echo off
REM ========================================
REM VMSI-SDM Auto Data Collection
REM ========================================

cd /d "%~dp0"

echo ========================================
echo VMSI-SDM Auto Data Collection
echo ========================================
echo.

REM Check if yfinance is installed
python -c "import yfinance" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] yfinance not found, installing...
    python -m pip install yfinance
)

REM Run auto collection
echo [INFO] Starting auto data collection...
python tools/auto_collect_data.py --symbols SPX NASDAQ QQQ --period 3y --interval 1wk

echo.
echo ========================================
echo [OK] Data collection complete!
echo ========================================
pause

