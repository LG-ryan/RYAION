@echo off
REM ═══════════════════════════════════════════════════════
REM ngrok Public URL 자동 확인
REM ═══════════════════════════════════════════════════════

echo.
echo [INFO] Checking ngrok URL...
echo.

REM ngrok API로 URL 확인
curl -s http://localhost:4040/api/tunnels > temp_ngrok.json 2>nul

if %ERRORLEVEL% EQU 0 (
    python -c "import json; data=json.load(open('temp_ngrok.json')); print('[OK] ngrok Public URL:'); print(data['tunnels'][0]['public_url'] if data['tunnels'] else '[ERROR] No tunnels found')"
    del temp_ngrok.json 2>nul
) else (
    echo [ERROR] ngrok not running or curl not available
    echo [INFO] Check manually: http://localhost:4040
)

echo.
echo [INFO] Copy this URL to TradingView Alert Webhook URL
echo [INFO] Format: https://abc123.ngrok-free.app/webhook/tv
echo.
pause

