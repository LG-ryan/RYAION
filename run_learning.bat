@echo off
REM ═══════════════════════════════════════════════════════
REM VMSI-SDM Optuna Learning (로컬 자동 실행)
REM Railway PostgreSQL 연결 + 무제한 학습!
REM ═══════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  VMSI-SDM Optuna Learning Loop (Local Unlimited)  ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo [INFO] Starting at: %date% %time%
echo.

REM ─────────────────────────────────────────────────────
REM 로컬 SQLite 사용 (DATABASE_URL 불필요)
REM ─────────────────────────────────────────────────────
echo [INFO] Using local SQLite database
echo [INFO] Database: vmsi_sdm.db
echo.

REM ─────────────────────────────────────────────────────
REM 작업 디렉토리 이동
REM ─────────────────────────────────────────────────────
cd /d "%~dp0"
echo [INFO] Working directory: %cd%
echo.

REM ─────────────────────────────────────────────────────
REM Python 환경 확인
REM ─────────────────────────────────────────────────────
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)
echo.

REM ─────────────────────────────────────────────────────
REM Optuna 학습 실행 (무제한 trials!)
REM trials: 학습 시도 횟수 (많을수록 좋은 파라미터 찾음)
REM timeout: 최대 실행 시간 (초)
REM ─────────────────────────────────────────────────────
echo [INFO] Running Optuna optimization...
echo [INFO] Trials: 200 (unlimited on local PC!)
echo [INFO] Timeout: 7200 seconds (2 hours)
echo.

python learner\tune.py --trials 200 --timeout 7200 --save-preset

REM ─────────────────────────────────────────────────────
REM 결과 확인
REM ─────────────────────────────────────────────────────
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] ═══════════════════════════════════════════
    echo [OK] Optimization completed successfully!
    echo [OK] ═══════════════════════════════════════════
    echo [OK] Best parameters saved to: presets\preset_B_candidate.json
    echo [OK] Check the file and apply to TradingView Indicator
    echo.
) else (
    echo.
    echo [ERROR] ═════════════════════════════════════════
    echo [ERROR] Optimization failed with code %ERRORLEVEL%
    echo [ERROR] ═════════════════════════════════════════
    echo [ERROR] Check the error messages above
    echo.
)

echo [INFO] Learning loop finished at: %time%
echo.
echo Press any key to exit...
pause > nul


