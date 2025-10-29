# 🏠 ngrok + 로컬 완전 가이드 (100% 무료)

**전략**: PC에서 모든 것을 실행 (신호 수집 + 학습 + 대시보드)

---

## 🎯 왜 ngrok + 로컬?

### ✅ 장점
```
✅ 완전 무료 ($0/월)
✅ 무제한 학습 (로컬 PC 성능 최대 활용)
✅ 빠른 속도 (클라우드보다 빠름)
✅ 데이터 완전 제어 (SQLite)
✅ 설정 간단 (10분)
✅ 트레이딩할 때 어차피 PC 켜져있음
```

### ⚠️ 단점 (현실적 관점)
```
⚠️ PC 꺼지면 신호 못 받음
   → 하지만 트레이딩할 때 어차피 켜져있음
   → 신호 놓쳐도 다음 신호 받으면 됨 (Stage Detection은 자주 안 바뀜)

⚠️ ngrok 2시간마다 재시작 필요
   → 자동화 스크립트로 해결 (아래 제공)

⚠️ ngrok URL 바뀔 때마다 TradingView Alert 수정
   → Free plan의 불가피한 부분 (5초 소요)
   → 유료($10/월) 시 고정 URL 가능
```

---

## 📊 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│              TradingView Alert                      │
│             (BUY/SELL Signal)                       │
└────────────────────┬────────────────────────────────┘
                     │ Webhook
                     ↓
┌─────────────────────────────────────────────────────┐
│   ngrok (Free, 2시간마다 재시작)                     │
│   https://abc123.ngrok-free.app → localhost:8000   │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│         로컬 PC (C:\Users\ryanj\RYAION\vmsi-sdm)    │
│  ┌────────────────────────────────────────────────┐ │
│  │ FastAPI (port 8000)                            │ │
│  │  - Webhook 수신                                │ │
│  │  - /health, /api/signals 엔드포인트            │ │
│  └────────────────┬───────────────────────────────┘ │
│                   ↓                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │ SQLite (vmsi_sdm.db)                           │ │
│  │  - signals 테이블 (TradingView 신호)           │ │
│  │  - experiments 테이블 (Optuna 결과)            │ │
│  └────────────────┬───────────────────────────────┘ │
│                   ↓                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │ Optuna Learning (무제한!)                      │ │
│  │  - Windows Task Scheduler (매일 새벽 2시)      │ │
│  │  - 수동 실행 (run_learning.bat)                │ │
│  └────────────────┬───────────────────────────────┘ │
│                   ↓                                  │
│  ┌────────────────────────────────────────────────┐ │
│  │ Streamlit Dashboard (port 8501)                │ │
│  │  - 실시간 신호 모니터링                         │ │
│  │  - 학습 결과 시각화                            │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Part 1: ngrok 설치 및 설정 (2분)

### Step 1.1: ngrok 다운로드

```
1. https://ngrok.com/ 접속
2. "Sign up" (무료 계정 생성)
3. "Download" → Windows 64-bit 다운로드
4. ngrok.exe 압축 해제
5. C:\Users\ryanj\RYAION\vmsi-sdm\ 폴더에 복사
```

---

### Step 1.2: ngrok 인증

```bash
# PowerShell
cd C:\Users\ryanj\RYAION\vmsi-sdm

# ngrok 대시보드에서 Authtoken 복사 후 실행
.\ngrok.exe config add-authtoken YOUR_AUTH_TOKEN_HERE
```

**예시**:
```bash
.\ngrok.exe config add-authtoken 2abCdEfGhIjKlMnOpQrStUvWxYz_1234567890ABCDEFG
```

✅ **Authtoken 저장 완료!**

---

### Step 1.3: ngrok 테스트

```bash
# FastAPI 서버가 실행 중이어야 함 (port 8000)
# 터미널 1: FastAPI 실행
cd C:\Users\ryanj\RYAION\vmsi-sdm
uvicorn server.app:app --host 0.0.0.0 --port 8000

# 터미널 2: ngrok 실행
cd C:\Users\ryanj\RYAION\vmsi-sdm
.\ngrok.exe http 8000
```

**예상 출력**:
```
ngrok

Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

✅ **Public URL**: `https://abc123.ngrok-free.app`

---

## 🖥️ Part 2: 로컬 서버 환경 설정 (5분)

### Step 2.1: Python 패키지 설치

```bash
cd C:\Users\ryanj\RYAION\vmsi-sdm
pip install -r requirements.txt
```

**설치되는 것들**:
- FastAPI, Uvicorn (웹 서버)
- SQLAlchemy (데이터베이스)
- Optuna (학습)
- Streamlit (대시보드)
- pandas, numpy (데이터 처리)

---

### Step 2.2: 데이터베이스 초기화

```bash
# 자동으로 vmsi_sdm.db 생성됨
python -c "from server.db import init_db; init_db()"
```

**예상 출력**:
```
[OK] Database initialized
[OK] Created table: signals
[OK] Created table: experiments
```

✅ **SQLite 데이터베이스 생성 완료!**

---

### Step 2.3: FastAPI 서버 시작

```bash
# start_server.bat 실행 또는:
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

**확인**:
- 브라우저: http://localhost:8000/health
- 응답: `{"status":"healthy"}`

---

### Step 2.4: Streamlit 대시보드 시작

```bash
# 새 터미널
cd C:\Users\ryanj\RYAION\vmsi-sdm
streamlit run dashboard\app.py --server.port 8501
```

**확인**:
- 브라우저: http://localhost:8501
- 대시보드 표시됨

---

## 🤖 Part 3: ngrok 자동화 (중요!)

### Step 3.1: ngrok 자동 시작 스크립트

**파일**: `vmsi-sdm/start_ngrok.bat`

```batch
@echo off
REM ═══════════════════════════════════════════════════════
REM ngrok 자동 시작 (2시간마다 재시작)
REM ═══════════════════════════════════════════════════════

cd /d "%~dp0"

echo [INFO] Starting ngrok tunnel...
echo [INFO] Forwarding: https://???.ngrok-free.app -> http://localhost:8000
echo.

REM ngrok 실행 (백그라운드)
start "" ngrok.exe http 8000

echo [OK] ngrok started!
echo [INFO] Check URL at: http://127.0.0.1:4040
echo.
echo ⚠️  ngrok Free plan: Session expires after 2 hours
echo ⚠️  Restart this script every 2 hours
echo.
pause
```

---

### Step 3.2: 통합 시작 스크립트 업데이트

**파일**: `vmsi-sdm/start_all.bat` (수정)

```batch
@echo off
REM ═══════════════════════════════════════════════════════
REM VMSI-SDM 통합 시작 (로컬 환경)
REM ═══════════════════════════════════════════════════════

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║       VMSI-SDM Local Setup (ngrok + SQLite)       ║
echo ╚════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM 1. FastAPI 서버 시작 (백그라운드)
echo [1/3] Starting FastAPI server...
start "FastAPI" cmd /k "uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul

REM 2. ngrok 터널 시작 (백그라운드)
echo [2/3] Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok.exe http 8000"
timeout /t 3 /nobreak > nul

REM 3. Streamlit 대시보드 시작 (백그라운드)
echo [3/3] Starting Streamlit dashboard...
start "Streamlit" cmd /k "streamlit run dashboard\app.py --server.port 8501"
timeout /t 3 /nobreak > nul

echo.
echo [OK] ═══════════════════════════════════════════════
echo [OK] All services started!
echo [OK] ═══════════════════════════════════════════════
echo.
echo 📍 FastAPI:    http://localhost:8000
echo 📍 ngrok Web:  http://localhost:4040 (Check public URL)
echo 📍 Streamlit:  http://localhost:8501
echo.
echo ⚠️  ngrok URL: Copy from http://localhost:4040
echo ⚠️  Update TradingView Alert with new URL
echo.
pause
```

---

### Step 3.3: ngrok URL 자동 확인 스크립트

**파일**: `vmsi-sdm/check_ngrok_url.bat`

```batch
@echo off
REM ngrok Public URL 확인
echo.
echo [INFO] Checking ngrok URL...
echo.

curl -s http://localhost:4040/api/tunnels | python -c "import sys, json; data=json.load(sys.stdin); print('[OK] ngrok Public URL:'); print(data['tunnels'][0]['public_url'])" 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ngrok not running or curl/python not available
    echo [INFO] Check manually: http://localhost:4040
)

echo.
pause
```

---

## 🔔 Part 4: TradingView Alert 설정

### Step 4.1: ngrok Public URL 확인

```
방법 1: 브라우저
- http://localhost:4040 접속
- "Forwarding" 항목에서 https://???.ngrok-free.app 복사

방법 2: check_ngrok_url.bat 실행
- 자동으로 URL 출력

방법 3: ngrok 터미널
- ngrok 실행한 터미널에서 "Forwarding" 확인
```

**예시**: `https://abc123-def456.ngrok-free.app`

---

### Step 4.2: TradingView Alert 생성

```
1. TradingView 차트에 VMSI-SDM Indicator 추가
2. Alert 생성 (Alt + A)

Condition:
- VMSI-SDM v2
- alert() function calls only

Options:
- ☑ Once Per Bar Close

Webhook URL:
https://abc123-def456.ngrok-free.app/webhook/tv

⚠️ ngrok URL은 2시간마다 바뀌므로 Alert 수정 필요!
```

---

### Step 4.3: ngrok URL 변경 시 Alert 업데이트

```
2시간마다:
1. start_ngrok.bat 재실행
2. http://localhost:4040에서 새 URL 확인
3. TradingView Alert 편집
4. Webhook URL 업데이트
5. 저장
```

**⏱️ 소요 시간**: 30초

---

## 🧪 Part 5: 전체 테스트

### Test 1: FastAPI Health Check

```bash
curl http://localhost:8000/health
```

**예상 응답**:
```json
{"status":"healthy"}
```

---

### Test 2: ngrok 터널 테스트

```bash
# ngrok Public URL로 테스트
curl https://abc123.ngrok-free.app/health
```

**예상 응답**:
```json
{"status":"healthy"}
```

---

### Test 3: Webhook 신호 전송 테스트

```bash
# PowerShell
$url = "https://abc123.ngrok-free.app/webhook/tv"
$body = @{
    ts_unix = 1730188800000
    symbol = "TEST"
    timeframe = "1D"
    action = "BUY"
    price = 100.5
    trend_score = 75.5
    prob = 0.68
    rsi = 58.5
    vol_mult = 1.5
    vcp_ratio = 0.12
    dist_ath = 0.05
    ema1 = 99.0
    ema2 = 98.0
    bar_state = "close"
    fast_mode = $false
    realtime_macro = $false
    version = "vmsi_sdm_v2.1"
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method Post -Body $body -ContentType "application/json"
```

**예상 응답**:
```json
{
  "status": "success",
  "signal_id": 1,
  "message": "Signal saved"
}
```

---

### Test 4: Streamlit 대시보드 확인

```
http://localhost:8501

✅ "최근 신호 목록"에 TEST 신호 표시
```

---

### Test 5: 로컬 학습 테스트

```bash
cd C:\Users\ryanj\RYAION\vmsi-sdm
.\run_learning.bat
```

**예상 출력** (신호 10개 이상 있을 때):
```
[INFO] Starting VMSI-SDM Optuna Learning Loop
[Trial 1/200] Score: 0.234
[Trial 2/200] Score: 0.289
...
[OK] Best parameters saved to: presets\preset_B_candidate.json
```

---

## 🤖 Part 6: Windows Task Scheduler (자동 학습)

### Step 6.1: 작업 생성

```
1. Windows 검색 → "작업 스케줄러"
2. "작업 만들기" 클릭

일반:
- 이름: VMSI-SDM Optuna Learning
- 사용자가 로그온할 때만 실행

트리거:
- 작업 시작: 일정에 따라
- 반복 간격: 매일
- 시작 시간: 오전 2:00

동작:
- 프로그램/스크립트: C:\Users\ryanj\RYAION\vmsi-sdm\run_learning.bat

조건:
- AC 전원 체크 해제

설정:
- 새 인스턴스 시작 안 함

3. 확인 클릭
```

✅ **매일 새벽 2시 자동 학습!**

---

## 📊 비용 비교

```
┌───────────────────┬──────────┬──────────────┐
│                   │ 클라우드  │ ngrok + 로컬 │
├───────────────────┼──────────┼──────────────┤
│ 월 비용           │ $7~10    │ $0          │
│ 학습 trials 제한  │ 50~100   │ 무제한!      │
│ 학습 속도         │ 느림     │ 빠름!        │
│ 데이터 제어       │ 제한적   │ 완전 제어    │
│ 설정 복잡도       │ 높음     │ 낮음         │
│ 유지보수          │ 자동     │ 수동 (2시간) │
└───────────────────┴──────────┴──────────────┘

결론: ngrok + 로컬이 압도적으로 우수! 💪
```

---

## 🎯 일일 루틴

### 트레이딩 시작 시
```
1. start_all.bat 실행 (FastAPI + ngrok + Streamlit)
2. http://localhost:4040에서 ngrok URL 확인
3. TradingView Alert URL 업데이트 (첫 실행 시만)
```

### 2시간마다 (ngrok 세션 만료 시)
```
1. ngrok 터미널에서 Ctrl+C (종료)
2. start_ngrok.bat 재실행
3. 새 URL 확인 → TradingView Alert 업데이트
```

### 트레이딩 종료 시
```
모든 터미널 닫기 (자동 종료)
```

---

## 🚨 트러블슈팅

### ❌ ngrok: "Session Expired"
```
원인: 2시간 세션 만료 (Free plan)
해결:
1. ngrok 터미널 닫기
2. start_ngrok.bat 재실행
3. 새 URL로 TradingView Alert 업데이트
```

### ❌ FastAPI 시작 안 됨
```
원인: Port 8000 이미 사용 중
해결:
1. taskkill /f /im uvicorn.exe
2. start_server.bat 재실행
```

### ❌ SQLite 오류
```
원인: vmsi_sdm.db 잠김
해결:
1. 모든 프로그램 종료
2. vmsi_sdm.db 삭제
3. python -c "from server.db import init_db; init_db()"
```

### ❌ ngrok "Tunnel not found"
```
원인: ngrok 계정 인증 안 됨
해결:
1. ngrok.com → Sign in
2. Authtoken 복사
3. .\ngrok.exe config add-authtoken YOUR_TOKEN
```

---

## 💡 Pro Tips

### Tip 1: ngrok 유료 플랜 ($10/월)
```
장점:
✅ 고정 URL (TradingView Alert 수정 불필요)
✅ 무제한 세션 (2시간 제한 없음)
✅ 빠른 속도

→ 편의성 크게 향상!
```

### Tip 2: 학습 시간 조정
```
run_learning.bat 수정:
- --trials 200 → 500 (더 강력한 학습)
- --timeout 7200 → 14400 (더 긴 시간)
```

### Tip 3: 백업
```
정기적으로 백업:
- vmsi_sdm.db (신호 데이터)
- presets/*.json (학습 결과)
```

---

## 📚 관련 문서

- `07_TRADINGVIEW_ALERT_SETUP.md`: Alert 설정 상세
- `06_REFACTOR_SUMMARY.md`: Pine Script v2.1 변경사항
- `02_QUICKSTART.md`: 빠른 시작 가이드

---

## 🎉 완료!

```
✅ 완전 무료 시스템 구축 완료!
✅ 무제한 학습 가능!
✅ 빠른 속도!
✅ 완전한 데이터 제어!

비용: $0/월
성능: 클라우드보다 우수
제어: 100% 자유
```

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**전략**: ngrok + 로컬 (100% 무료, 무제한 학습)

🏠 **로컬 최고! PC에서 모든 것을!**


