@echo off
REM ========================================
REM Auto Collect Data + Learn (for Task Scheduler)
REM ========================================

cd /d "%~dp0"

echo ========================================
echo VMSI-SDM Auto Collect + Learn
echo ========================================
echo Started: %DATE% %TIME%
echo.

REM 1. Start FastAPI if not running
echo [1/3] Checking FastAPI server...
tasklist /FI "WINDOWTITLE eq FastAPI*" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo [INFO] Starting FastAPI server...
    start "FastAPI" cmd /k "python -m uvicorn server.app:app --host 0.0.0.0 --port 8000"
    timeout /t 5 /nobreak > nul
) else (
    echo [OK] FastAPI already running
)

REM 2. Collect data
echo.
echo [2/3] Collecting market data...
python tools/auto_collect_data.py --symbols SPX NASDAQ QQQ --period 3y --interval 1wk

REM 3. Run learning
echo.
echo [3/3] Running Optuna learning...
python learner/tune.py --signal-type BUY --trials 30 --timeout 1800

echo.
echo ========================================
echo [OK] Auto collect + learn complete!
echo ========================================
echo Ended: %DATE% %TIME%

