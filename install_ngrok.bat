@echo off
REM ═══════════════════════════════════════════════════════
REM ngrok 설치 가이드
REM ═══════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║              ngrok Installation Guide              ║
echo ╚════════════════════════════════════════════════════╝
echo.

echo [Step 1] 브라우저에서 ngrok 다운로드
echo.
echo 1. 이 URL을 브라우저에 복사:
echo    https://ngrok.com/download
echo.
echo 2. "Windows (64-bit)" 클릭하여 다운로드
echo.
echo 3. 다운로드된 ngrok.zip 파일을 찾아서
echo    이 폴더로 복사: C:\Users\ryanj\RYAION\vmsi-sdm
echo.
echo 4. ngrok.zip 우클릭 -^> "압축 풀기"
echo.
echo 5. ngrok.exe 파일이 이 폴더에 있는지 확인:
echo    C:\Users\ryanj\RYAION\vmsi-sdm\ngrok.exe
echo.
pause

echo.
echo [Step 2] ngrok Authtoken 설정
echo.
echo Authtoken이 있으면 입력하고 Enter:
set /p TOKEN="Token: "

if "%TOKEN%"=="" (
    echo [ERROR] Token이 입력되지 않았습니다
    pause
    exit /b 1
)

echo.
echo [INFO] Setting authtoken...
ngrok.exe config add-authtoken %TOKEN%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] ═══════════════════════════════════════════════
    echo [OK] ngrok 설치 완료!
    echo [OK] ═══════════════════════════════════════════════
    echo.
    echo 다음 단계: start_all.bat 실행
) else (
    echo.
    echo [ERROR] ngrok.exe를 찾을 수 없습니다
    echo [ERROR] Step 1을 먼저 완료하세요
)

echo.
pause


