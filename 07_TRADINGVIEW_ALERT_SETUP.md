# 🔔 TradingView Alert 설정 가이드

**목적**: VMSI-SDM Indicator에서 BUY/SELL 신호 발생 시 Render Webhook 서버로 자동 전송

---

## 📋 사전 준비

### ✅ 완료해야 할 것들
- [x] Render Web Service 배포 (FastAPI 서버)
- [x] Render PostgreSQL 데이터베이스 생성
- [x] Streamlit Cloud 대시보드 배포
- [x] Indicator Pine Script 업로드 (v2.1)
- [ ] **TradingView Alert 설정** ← 지금 이 단계!

### 📌 필요한 정보
1. **Webhook URL**: Render Web Service URL
   - 형식: `https://ryaion.onrender.com/webhook/tv`
   - Render 대시보드에서 확인 가능

---

## 🎯 Step 1: Indicator를 차트에 추가

### 1.1. TradingView 접속
```
1. https://www.tradingview.com/ 접속
2. 로그인
3. 원하는 차트 열기 (예: SPY, QQQ, AAPL 등)
```

### 1.2. Indicator 추가
```
1. 상단 "Indicators" 버튼 클릭
2. 검색창에 "VMSI-SDM v2" 입력
3. "My Scripts" 탭에서 "VMSI-SDM v2 (Volde Momentum Stage Indicator)" 선택
4. 차트에 Indicator가 표시됨
```

### 1.3. 설정 확인
```
Indicator 설정 (톱니바퀴 아이콘):

📌 파라미터 설정
- EMA1 Length: 20
- EMA2 Length: 50
- RSI Length: 14
- VCP Length: 20
- Hysteresis Length: 5  (신호 안정화)
- Cooldown Bars: 10     (중복 신호 방지)

📌 모드 설정
- Fast Mode: OFF (기본값, 안정적 신호)
- Use Real-time Macro Data: OFF (시뮬레이션 사용)

📌 매크로 심볼 (선택사항)
- VIX Symbol: CBOE:VIX
- DXY Symbol: TVC:DXY
- US10Y Symbol: TVC:US10Y
- HYG Symbol: AMEX:HYG
- IEF Symbol: NASDAQ:IEF

📌 테이블 설정
- Panel Position: Top Right (우측 상단)
- Panel Size: Normal

📌 Webhook
- Enable Webhook: ON ✅ (중요!)
- Webhook URL: (비워두기 - Alert 설정 시 입력)
```

---

## 🚨 Step 2: Alert 생성 (중요!)

### 2.1. Alert 창 열기
```
방법 1: 차트 우클릭 → "Add Alert"
방법 2: 상단 시계 아이콘 ⏰ 클릭
방법 3: 단축키: Alt + A (Windows) / Option + A (Mac)
```

### 2.2. Alert 조건 설정
```
┌─────────────────────────────────────────────┐
│ Create Alert                                │
├─────────────────────────────────────────────┤
│ Condition                                   │
│ ┌─────────────────────────────────────────┐ │
│ │ VMSI-SDM v2 ▼                           │ │  ← Indicator 선택
│ │ alert() function calls only ▼           │ │  ← 이 옵션 선택 (중요!)
│ └─────────────────────────────────────────┘ │
│                                             │
│ Options                                     │
│ ☑ Once Per Bar Close                       │  ← 체크 (중요!)
│                                             │
│ Expiration                                  │
│ ○ Open-ended (no expiration)               │  ← 선택
│                                             │
│ Alert name                                  │
│ ┌─────────────────────────────────────────┐ │
│ │ VMSI-SDM BUY/SELL Signal (SPY)          │ │  ← 자유롭게 입력
│ └─────────────────────────────────────────┘ │
│                                             │
│ Alert message                               │
│ ┌─────────────────────────────────────────┐ │
│ │ {{plot("alert_msg")}}                   │ │  ← Pine Script JSON 사용
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### 2.3. Webhook 설정 (핵심!)
```
Notifications 섹션에서:

☐ Notify on App       (선택사항)
☐ Show popup          (선택사항)
☐ Send email          (선택사항)
☐ Play sound          (선택사항)
☑ Webhook URL         ← 이것만 필수!

Webhook URL 입력:
┌─────────────────────────────────────────────┐
│ https://ryaion.onrender.com/webhook/tv      │
└─────────────────────────────────────────────┘
```

**⚠️ 중요**: 
- Webhook URL은 **Render Web Service URL + `/webhook/tv`**
- 예: `https://your-service.onrender.com/webhook/tv`
- Render 대시보드 → Web Service → 상단 URL 복사

---

## 📝 Step 3: Alert 설정 체크리스트

### ✅ 필수 확인 사항
```
[ ] Condition: "alert() function calls only" 선택됨
[ ] Options: "Once Per Bar Close" 체크됨
[ ] Alert message: "{{plot("alert_msg")}}" 입력됨
[ ] Webhook URL: Render URL 정확히 입력됨
[ ] Indicator 설정: "Enable Webhook" ON
```

### ❌ 흔한 실수
```
1. "Any alert() function call" 대신 "alert() function calls only" 선택 안 함
2. Alert message를 직접 입력 (JSON 무시)
3. Webhook URL 마지막에 /webhook/tv 빠뜨림
4. Indicator 설정에서 "Enable Webhook" OFF
5. "Once Per Bar Close" 체크 안 함 (실시간 신호 남발)
```

---

## 🧪 Step 4: 테스트

### 4.1. 수동 테스트 (개발 환경)
```bash
# 터미널에서 실행
cd C:\Users\ryanj\RYAION\vmsi-sdm
curl -X POST http://localhost:8000/webhook/tv `
  -H "Content-Type: application/json" `
  -d '{
    "ts_unix":1730188800000,
    "symbol":"TEST",
    "timeframe":"1D",
    "action":"BUY",
    "price":100.5,
    "trend_score":75.5,
    "prob":0.68,
    "rsi":58.5,
    "vol_mult":1.5,
    "vcp_ratio":0.12,
    "dist_ath":0.05,
    "ema1":99.0,
    "ema2":98.0,
    "bar_state":"close",
    "fast_mode":false,
    "realtime_macro":false,
    "version":"vmsi_sdm_v2.1"
  }'
```

### 4.2. 실제 신호 대기
```
1. TradingView 차트를 열어둡니다
2. 우측 상단 패널에서 "Stage" 변화를 관찰합니다
3. BUY 또는 SELL 신호 발생 시:
   - 차트에 초록색 "BUY" 또는 빨간색 "SELL" 라벨 표시
   - TradingView Alert 발동 (알림 탭에서 확인)
   - Webhook이 Render 서버로 전송됨
```

### 4.3. 서버 로그 확인
```
Render 대시보드:
1. Web Service → "Logs" 탭
2. 실시간 로그에서 다음 확인:
   - "POST /webhook/tv" (요청 수신)
   - "Signal saved: id=..." (DB 저장 성공)
```

### 4.4. Streamlit 대시보드 확인
```
https://your-app.streamlit.app

1. "최근 신호 목록" 테이블에서 새 신호 확인
2. "신호 분석" 차트에서 시각화 확인
3. "Feature 분포" 그래프에서 TrendScore, Prob 등 확인
```

---

## 🔍 트러블슈팅

### ❌ Alert가 발동되지 않음
```
원인 1: Indicator 설정에서 "Enable Webhook" OFF
해결: Indicator 설정 → Webhook → Enable Webhook: ON

원인 2: Alert 조건이 "Any alert() function call"
해결: Alert 수정 → Condition: "alert() function calls only"

원인 3: 신호 조건이 충족되지 않음 (Stage Detection은 보수적)
해결: 
  - Fast Mode ON으로 테스트 (신호 빠름)
  - 더 짧은 타임프레임 사용 (1H, 4H)
  - Hysteresis Length 줄이기 (5 → 3)
```

### ❌ Webhook이 전송되지 않음
```
원인 1: Webhook URL이 잘못됨
해결: Render 대시보드에서 정확한 URL 복사 + /webhook/tv

원인 2: Render 서버가 sleep 상태 (Free plan)
해결: 
  - Render 대시보드 → Web Service → "Events" 탭 확인
  - Keep Alive 워크플로우 활성화 (이미 설정됨)
  - 브라우저에서 https://ryaion.onrender.com/health 접속 (wake up)

원인 3: Alert message가 잘못됨
해결: Alert 수정 → Message: {{plot("alert_msg")}}
```

### ❌ 서버는 받았지만 DB에 저장 안 됨
```
원인 1: DATABASE_URL 환경변수 미설정
해결: Render 대시보드 → Environment → DATABASE_URL 확인

원인 2: JSON 스키마 불일치
해결: 
  - Indicator 버전 확인 (v2.1)
  - server/schemas.py와 일치하는지 확인
  - Render 로그에서 에러 메시지 확인
```

### ❌ Streamlit에 신호가 안 보임
```
원인 1: Streamlit이 External Database URL을 사용 안 함
해결: Streamlit Cloud → Secrets → DATABASE_URL 확인 (oregon-postgres.render.com 포함)

원인 2: 캐시 문제
해결: Streamlit 앱 → 우측 상단 ⋮ → "Reboot app"

원인 3: 조회 기간 밖
해결: 대시보드 → "조회 기간" 슬라이더 → 더 긴 기간 선택 (30일, 90일)
```

---

## 📊 예상 Alert JSON (v2.1)

```json
{
  "ts_unix": 1730188800000,
  "symbol": "SPY",
  "timeframe": "1D",
  "action": "BUY",
  "price": 450.25,
  "trend_score": 82.50,
  "prob": 0.7234,
  "rsi": 58.32,
  "vol_mult": 1.82,
  "vcp_ratio": 0.1234,
  "dist_ath": 0.0567,
  "ema1": 448.20,
  "ema2": 445.80,
  "bar_state": "close",
  "fast_mode": false,
  "realtime_macro": false,
  "version": "vmsi_sdm_v2.1"
}
```

---

## 🎯 다음 단계

Alert가 정상 작동하면:

1. **Labeler 실행** (수동):
   ```bash
   cd C:\Users\ryanj\RYAION\vmsi-sdm
   python -c "from server.labeler import label_all_signals; label_all_signals()"
   ```

2. **Optuna Learning 자동 실행** (매일 오전 2시 UTC):
   - GitHub Actions가 자동으로 실행
   - 충분한 데이터(신호 10개 이상) 수집 후 학습 시작
   - `preset_B_candidate.json` 자동 업데이트

3. **Preset 적용** (수동):
   - `preset_B_candidate.json` → Indicator 설정에 복사
   - 백테스트 후 성능 확인
   - 실거래 적용 여부 결정

---

## 💡 팁

### 🎓 Stage Detection 이해하기
```
VMSI-SDM은 "데이트레이딩"이 아닌 "스윙 트레이딩"을 위한 시스템입니다.

신호 발생 빈도:
- Fast Mode OFF: 주~월 단위 (보수적, 안정적)
- Fast Mode ON: 일~주 단위 (빠르지만 노이즈 많음)

권장 설정:
- 타임프레임: 1D (일봉)
- Hysteresis: 5 (안정화)
- Cooldown: 10 (중복 방지)
```

### 🔔 Alert 관리
```
1. 여러 심볼에 Alert 설정 가능 (SPY, QQQ, AAPL 등)
2. 심볼마다 Alert 이름 구분 ("VMSI-SDM BUY/SELL (SPY)")
3. 모든 Alert의 Webhook URL은 동일
4. 서버가 symbol 필드로 자동 구분
```

### 📈 성능 최적화
```
1. 처음 1~2주: 데이터 수집 (Alert만 작동)
2. 2주 후: Labeler 수동 실행 (미래 수익률 계산)
3. 신호 10개 이상: Optuna Learning 시작 (자동)
4. 1개월 후: 충분한 학습 데이터로 최적 파라미터 도출
```

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**버전**: VMSI-SDM v2.1

**관련 문서**:
- `04_TRADINGVIEW_SETUP.md`: TradingView 기본 설정
- `05_CLOUD_DEPLOYMENT.md`: 클라우드 배포 가이드
- `06_REFACTOR_SUMMARY.md`: Pine Script v2.1 변경사항

