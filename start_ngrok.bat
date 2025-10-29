@echo off
REM ═══════════════════════════════════════════════════════
REM ngrok 터널 시작 (TradingView Webhook용)
REM ═══════════════════════════════════════════════════════

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║            ngrok Tunnel Starting...                ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo [INFO] Forwarding: https://???.ngrok-free.app -^> http://localhost:8000
echo [INFO] Web Interface: http://localhost:4040
echo.

REM ngrok 실행
ngrok.exe http 8000

REM ngrok 종료 시 (Ctrl+C or 세션 만료)
echo.
echo [INFO] ngrok session ended
echo [INFO] Restart this script to get new URL
echo.
pause

