@echo off
chcp 65001 > nul
title 포트 문제 해결

echo.
echo ============================================================
echo   🔧 포트 9333 문제 해결
echo ============================================================
echo.

echo [1] Chrome 프로세스 강제 종료...
taskkill /F /IM chrome.exe /T >nul 2>&1
taskkill /F /IM chromedriver.exe /T >nul 2>&1
echo ✅ 완료

echo.
echo [2] 포트 9333 사용 중인 프로세스 확인...
netstat -ano | findstr "9333"

echo.
echo [3] 포트 9333 점유 프로세스 강제 종료...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "9333"') do (
    echo 종료 중: PID %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo ✅ 완료

echo.
echo [4] 최종 확인...
timeout /t 2 /nobreak >nul
netstat -ano | findstr "9333" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  포트가 여전히 사용 중입니다.
    echo.
    echo 💡 PC를 재부팅하는 것을 권장합니다.
) else (
    echo ✅ 포트 9333이 정리되었습니다!
    echo.
    echo 이제 all_in_one.bat를 실행하세요.
)

echo.
pause

