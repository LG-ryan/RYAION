# 🏗️ **VMSI-SDM v5 Real Data Architecture**

## 개요

**문제점**: ngrok 주소 변동, 웹훅 의존성, 샘플 데이터의 비현실성

**해결책**: 실시간 시장 데이터 기반 자동 학습 시스템

---

## 🔄 **새로운 아키텍처**

```
┌─────────────────────────────────────────────────────────────────┐
│  yfinance (Yahoo Finance API)                                   │
│  - 무료, 무제한                                                 │
│  - SPX, NASDAQ, QQQ 등 주요 지수                               │
│  - 실시간 데이터 + 과거 데이터                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  auto_collect_data.py                                           │
│  - 자동 데이터 다운로드                                        │
│  - 지표 계산 (EMA, RSI, ATR, VCP, Trend Score)                │
│  - 신호 생성 (v5 Final 로직)                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Server (http://localhost:8000)                         │
│  - 신호 저장 (SQLite)                                          │
│  - 라벨링 (백그라운드)                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Optuna Learning (learner/tune.py)                              │
│  - 실제 데이터 기반 파라미터 최적화                            │
│  - BUY/SELL 신호 품질 개선                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Streamlit Dashboard                                            │
│  - 실시간 신호 모니터링                                        │
│  - CSV 업로드 기능                                             │
│  - 애널리스트 리포트                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 **주요 기능**

### **1. 자동 데이터 수집 (yfinance)**

```bash
# 수동 실행
python tools/auto_collect_data.py --symbols SPX NASDAQ QQQ --period 3y --interval 1wk

# 또는 배치 파일
run_auto_collect.bat
```

**특징:**
- Yahoo Finance에서 실시간 데이터 다운로드
- 무료, API 키 불필요
- 과거 데이터 최대 10년 지원
- 다양한 간격 (1분, 1시간, 1일, 1주, 1개월)

---

### **2. CSV 업로드 (대시보드)**

```
1. Streamlit 대시보드 접속
2. 사이드바 "📤 데이터 업로드" 섹션
3. TradingView CSV 파일 업로드
4. "CSV 임포트 시작" 버튼 클릭
```

**지원 형식:**
- TradingView Strategy Tester 내보내기 CSV
- `SP_SPX, 1W.csv` 형식
- Columns: time, open, high, low, close, Volume, EMA1, EMA2

---

### **3. 자동 학습 스케줄 (Windows)**

```bash
# 스케줄 설정 (관리자 권한 필요)
schedule_auto_learn.bat
```

**실행 내용:**
1. FastAPI 서버 시작 (중지되어 있으면)
2. yfinance로 SPX, NASDAQ, QQQ 데이터 수집 (최근 3년)
3. Optuna 학습 (30 trials, 30분 timeout)
4. 매일 새벽 3시 자동 실행

**스케줄 관리:**
```powershell
# 작업 확인
schtasks /query /tn "VMSI_SDM_Auto_Learn"

# 수동 실행
schtasks /run /tn "VMSI_SDM_Auto_Learn"

# 작업 삭제
schtasks /delete /tn "VMSI_SDM_Auto_Learn" /f
```

---

## 🚀 **사용 방법**

### **Step 1: 초기 데이터 수집**

```bash
# 서버 시작
start_all.bat

# 실제 데이터 수집 (방법 1: yfinance)
run_auto_collect.bat

# 또는 (방법 2: CSV 업로드)
# 1. TradingView에서 CSV 내보내기
# 2. 대시보드에서 CSV 업로드
```

---

### **Step 2: 대시보드 확인**

```
http://localhost:8501
```

**확인사항:**
- ✅ 신호 목록에 실제 날짜 데이터
- ✅ Buy/Sell 신호 균형 (Buy:Sell = 약 60:40)
- ✅ 애널리스트 리포트 생성

---

### **Step 3: 자동 학습 설정 (선택)**

```bash
# 관리자 권한으로 실행
schedule_auto_learn.bat
```

**효과:**
- 매일 새벽 3시 자동 학습
- 파라미터 지속적 최적화
- 신호 품질 개선

---

## 📊 **데이터 소스 비교**

| 방법 | 장점 | 단점 | 권장 |
|------|------|------|------|
| **yfinance** | • 무료 무제한<br>• 자동화 쉬움<br>• 실시간 데이터 | • 지표 직접 계산<br>• API 제한 가능성 | ⭐⭐⭐⭐⭐ |
| **CSV 업로드** | • TradingView 지표 활용<br>• 정확한 신호 재현 | • 수동 작업<br>• 자동화 어려움 | ⭐⭐⭐ |
| **TradingView 웹훅** | • 실시간 신호<br>• Pine Script 직접 연동 | • ngrok 주소 변동<br>• PC 항상 켜야 함 | ⭐⭐ |

---

## 🔧 **설정 파일**

### **tools/auto_collect_data.py**

핵심 파라미터:
```python
# v5 Final 조건과 동일
buy_condition = (
    row['ema1'] > row['ema2'] and 
    row['rsi'] > 45 and 
    row['vol_mult'] > 1.0 and
    row['trend_score'] >= 50
)

sell_condition = (
    row['ema1'] < row['ema2'] and 
    row['rsi'] < 55 and 
    row['vol_mult'] > 1.0 and
    row['trend_score'] <= 50
)
```

### **schedule_auto_learn.bat**

변경 가능 항목:
```batch
set SCHEDULE_TIME=03:00  ← 실행 시간 변경
```

---

## 🎯 **Pine Script 파라미터 동기화**

yfinance 데이터로 학습한 결과를 Pine Script에 반영:

```pine
// v5 Final Indicator
trend_score_buy = input.float(50, ...)   ← Optuna 최적값
trend_score_sell = input.float(50, ...)  ← Optuna 최적값
rsi_buy_min = input.float(45, ...)       ← Optuna 최적값
rsi_sell_max = input.float(55, ...)      ← Optuna 최적값
vol_mult_buy = input.float(1.0, ...)     ← Optuna 최적값
vol_mult_sell = input.float(1.0, ...)    ← Optuna 최적값
```

---

## 📝 **Troubleshooting**

### **Q1: yfinance 설치 오류**

```bash
python -m pip install --upgrade yfinance
```

### **Q2: CSV 임포트 실패**

```
확인사항:
1. FastAPI 서버 실행 중인지 확인
2. CSV 파일 형식이 올바른지 확인
3. time 컬럼이 Unix timestamp인지 확인
```

### **Q3: 스케줄 작업 실패**

```powershell
# 작업 로그 확인
Get-EventLog -LogName Application -Source "Task Scheduler" -Newest 10
```

---

## 🔮 **향후 계획**

1. ✅ yfinance 기반 자동 데이터 수집
2. ✅ CSV 업로드 기능
3. ✅ 자동 학습 스케줄러
4. ⏳ Alpha Vantage API 추가 (무료 대체)
5. ⏳ Polygon.io 통합 (프리미엄 데이터)
6. ⏳ 실시간 WebSocket 데이터 스트리밍

---

## 📚 **관련 문서**

- `00_HOW_TO_USE.md` - 기본 사용법
- `07_TRADINGVIEW_ALERT_SETUP.md` - TradingView 알럿 설정
- `08_NGROK_LOCAL_SETUP.md` - ngrok 로컬 설정 (레거시)
- `EXPORT_CSV_GUIDE.md` - CSV 내보내기 가이드

---

**Last Updated**: 2025-10-29  
**Version**: v5 Real Data Architecture  
**Status**: ✅ Production Ready

