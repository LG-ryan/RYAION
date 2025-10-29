@echo off
REM ═══════════════════════════════════════════════════════
REM VMSI-SDM 전체 재시작 (모든 프로세스 종료 후 재시작)
REM ═══════════════════════════════════════════════════════

echo.
echo [INFO] Stopping all VMSI-SDM processes...
echo.

REM 1. Python 프로세스 종료 (FastAPI, Streamlit)
taskkill /F /IM python.exe 2>nul
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM streamlit.exe 2>nul

REM 2. ngrok 종료
taskkill /F /IM ngrok.exe 2>nul

timeout /t 2 /nobreak > nul

echo.
echo [INFO] Starting all services...
echo.

REM 3. start_all.bat 실행
call "%~dp0start_all.bat"


