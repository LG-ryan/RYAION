@echo off
echo ============================================================
echo VMSI-SDM 시스템 시작
echo ============================================================
echo.
echo [고정 포트]
echo   - API 서버: http://localhost:8000
echo   - 대시보드: http://localhost:8501
echo.
echo ============================================================
echo.

cd /d %~dp0

echo [1/2] API 서버 시작 중... (포트 8000)
start "VMSI-SDM API Server" cmd /k "python -m uvicorn server.app:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] 대시보드 시작 중... (포트 8501)
start "VMSI-SDM Dashboard" cmd /k "python -m streamlit run dashboard\app.py --server.port 8501"

echo.
echo ============================================================
echo 시작 완료!
echo ============================================================
echo.
echo 접속 주소:
echo   - API 문서: http://localhost:8000/docs
echo   - 대시보드: http://localhost:8501
echo.
echo 서버 종료: 각 창에서 Ctrl+C
echo ============================================================
echo.
pause


