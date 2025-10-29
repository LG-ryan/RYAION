@echo off
REM ========================================
REM Schedule Auto Learning (Windows Task Scheduler)
REM ========================================

cd /d "%~dp0"

set TASK_NAME=VMSI_SDM_Auto_Learn
set SCRIPT_PATH=%CD%\run_auto_collect_and_learn.bat
set SCHEDULE_TIME=03:00

echo ========================================
echo Schedule Auto Learning Task
echo ========================================
echo.
echo Task Name: %TASK_NAME%
echo Script:    %SCRIPT_PATH%
echo Schedule:  Daily at %SCHEDULE_TIME%
echo.

REM Delete existing task if exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Deleting existing task...
    schtasks /delete /tn "%TASK_NAME%" /f
)

REM Create new task
echo [INFO] Creating new task...
schtasks /create /tn "%TASK_NAME%" /tr "\"%SCRIPT_PATH%\"" /sc daily /st %SCHEDULE_TIME% /rl highest /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [OK] Task scheduled successfully!
    echo ========================================
    echo.
    echo The system will auto-collect data and learn:
    echo - Daily at %SCHEDULE_TIME%
    echo - Symbols: SPX, NASDAQ, QQQ
    echo - Period: Last 3 years
    echo - Interval: 1 week
    echo.
    echo To view the task:
    echo   schtasks /query /tn "%TASK_NAME%"
    echo.
    echo To run the task manually:
    echo   schtasks /run /tn "%TASK_NAME%"
    echo.
    echo To delete the task:
    echo   schtasks /delete /tn "%TASK_NAME%" /f
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Failed to create task!
    echo ========================================
    echo.
    echo Try running this script as Administrator.
    echo.
)

pause

