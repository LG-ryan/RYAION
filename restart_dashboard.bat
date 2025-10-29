@echo off
echo ============================================================
echo 대시보드 완전 재시작 중...
echo ============================================================
echo.

cd /d %~dp0

echo [1/3] 기존 Streamlit 프로세스 종료 중...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*" 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] 캐시 정리 중...
if exist ".streamlit" rmdir /s /q .streamlit
if exist "__pycache__" rmdir /s /q __pycache__
if exist "dashboard\__pycache__" rmdir /s /q dashboard\__pycache__

echo [3/3] 대시보드 시작 중... (포트 8501)
start "VMSI-SDM Dashboard (NEW)" python -m streamlit run dashboard\app.py --server.port 8501 --server.headless true

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo 대시보드 재시작 완료!
echo ============================================================
echo.
echo 브라우저에서 접속:
echo   http://localhost:8501
echo.
echo 캐시 완전 삭제: Ctrl+Shift+Delete (브라우저)
echo ============================================================
pause


