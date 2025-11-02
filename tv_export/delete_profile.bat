@echo off
chcp 65001 > nul
title 프로필 삭제

echo.
echo ============================================================
echo   🗑️  복사된 Chrome 프로필 삭제
echo ============================================================
echo.
echo 📌 이 도구는:
echo   - 복사된 Chrome 프로필을 삭제합니다
echo   - 다음 실행 시 새로 복사됩니다
echo.
echo 🤔 언제 사용하나요?
echo   - 로그인이 안 될 때
echo   - 프로필 문제가 있을 때
echo   - 새로 복사하고 싶을 때
echo.
pause

set "PROFILE_PATH=%TEMP%\ChromeProfile_TVExport"

echo.
echo 프로필 삭제 중...
echo 경로: %PROFILE_PATH%
echo.

if exist "%PROFILE_PATH%" (
    rmdir /S /Q "%PROFILE_PATH%"
    echo ✅ 프로필 삭제 완료!
    echo.
    echo 다음 실행 시 새로 복사됩니다.
) else (
    echo ℹ️  삭제할 프로필이 없습니다.
)

echo.
pause

