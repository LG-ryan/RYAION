@echo off
REM ═══════════════════════════════════════════════════════
REM VMSI-SDM 통합 시작 (로컬 환경)
REM FastAPI + ngrok + Streamlit
REM ═══════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║       VMSI-SDM Local Setup (ngrok + SQLite)       ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM 1. FastAPI 서버 시작 (백그라운드)
echo [1/3] Starting FastAPI server...
start "FastAPI" cmd /k "uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul

REM 2. ngrok 터널 시작 (백그라운드)
echo [2/3] Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok.exe http 8000"
timeout /t 3 /nobreak > nul

REM 3. Streamlit 대시보드 시작 (백그라운드)
echo [3/3] Starting Streamlit dashboard...
start "Streamlit" cmd /k "streamlit run dashboard\app.py --server.port 8501"
timeout /t 3 /nobreak > nul

echo.
echo [OK] ═══════════════════════════════════════════════
echo [OK] All services started!
echo [OK] ═══════════════════════════════════════════════
echo.
echo 📍 FastAPI:    http://localhost:8000
echo 📍 ngrok Web:  http://localhost:4040 (Check public URL)
echo 📍 Streamlit:  http://localhost:8501
echo.
echo ⚠️  ngrok URL: Copy from http://localhost:4040
echo ⚠️  Update TradingView Alert with new URL
echo ⚠️  ngrok Free: Session expires after 2 hours
echo.
echo 💡 Tip: Run check_ngrok_url.bat to get current URL
echo.
pause
