@echo off
REM VMSI-SDM Windows 초기화 스크립트

echo ============================================================
echo 🚀 VMSI-SDM 프로젝트 초기화
echo ============================================================
echo.

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않거나 PATH에 없습니다.
    echo    Python 3.9 이상을 설치하고 PATH에 추가하세요.
    echo    다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python 확인 완료
python --version

echo.
echo [1/5] 가상환경 생성 중...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ 가상환경 생성 실패
    pause
    exit /b 1
)
echo ✓ 가상환경 생성 완료

echo.
echo [2/5] 가상환경 활성화 중...
call venv\Scripts\activate
echo ✓ 가상환경 활성화 완료

echo.
echo [3/5] 패키지 설치 중...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)
echo ✓ 패키지 설치 완료

echo.
echo [4/5] 환경변수 파일 생성 중...
if not exist .env (
    copy env.example .env
    echo ✓ .env 파일 생성 완료
) else (
    echo ✓ .env 파일 이미 존재
)

echo.
echo [5/5] 데이터베이스 초기화 중...
python -c "from server.db import init_db; init_db()"
if %errorlevel% neq 0 (
    echo ❌ 데이터베이스 초기화 실패
    pause
    exit /b 1
)
echo ✓ 데이터베이스 초기화 완료

echo.
echo ============================================================
echo 🎉 초기화 완료!
echo ============================================================
echo.
echo 📋 다음 단계:
echo.
echo   1. 서버 실행:
echo      python server\app.py
echo.
echo   2. 대시보드 실행 (새 터미널):
echo      streamlit run dashboard\app.py
echo.
echo   3. TradingView 연결:
echo      pine\indicator_sdm_v2.pine 복사 후 TradingView에 추가
echo.
echo   자세한 내용: QUICKSTART.md 참조
echo.
echo ============================================================
pause


