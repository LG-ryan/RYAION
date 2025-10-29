@echo off
chcp 65001 > nul
echo ========================================
echo VMSI-SDM FastAPI 서버 시작
echo ========================================
echo.

cd /d %~dp0

echo [1/2] 데이터베이스 초기화 중...
python server\db.py
if errorlevel 1 (
    echo.
    echo [ERROR] 데이터베이스 초기화 실패!
    pause
    exit /b 1
)

echo.
echo [2/2] FastAPI 서버 시작 중...
echo.
echo 서버 주소: http://localhost:8000
echo API 문서: http://localhost:8000/docs
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload

