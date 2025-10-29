# 🎯 VMSI-SDM 사용 가이드 (초보자용)

**목적**: TradingView 신호를 자동으로 받아서 최적의 매매 파라미터를 학습하는 시스템

---

## 🧩 전체 시스템 구조 (쉽게 이해하기)

```
┌─────────────────────────────────────────────────────────────┐
│                    TradingView 차트                          │
│  (Pine Script Indicator: VMSI-SDM v2)                       │
│                                                              │
│  → BUY/SELL 신호 발생!                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ Webhook (인터넷)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   ngrok 터널                                 │
│  https://70d55bc3c9e5.ngrok-free.app                        │
│  (인터넷 → 로컬 PC 연결)                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              로컬 PC (C:\Users\ryanj\RYAION\vmsi-sdm)       │
│                                                              │
│  [1] FastAPI 서버 (port 8000)                               │
│      → 신호를 받아서 저장                                    │
│                                                              │
│  [2] SQLite 데이터베이스 (vmsi_sdm.db)                      │
│      → 모든 신호가 여기에 저장됨                             │
│                                                              │
│  [3] Streamlit 대시보드 (port 8501)                         │
│      → 저장된 신호를 예쁘게 보여줌                           │
│                                                              │
│  [4] Optuna 학습 (run_learning.bat)                         │
│      → 저장된 신호로 최적 파라미터 찾기                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 매일 해야 할 일 (간단!)

### 아침에 PC 켤 때:

**1단계: 모든 서비스 시작**
```
폴더: C:\Users\ryanj\RYAION\vmsi-sdm
파일: start_all.bat 더블클릭!
```

**실행되는 것들:**
- ✅ FastAPI 서버 (검은 창 1개)
- ✅ ngrok 터널 (검은 창 1개)
- ✅ Streamlit 대시보드 (브라우저 자동 열림)

**2단계: ngrok URL 확인**
```
브라우저: http://localhost:4040 열기
"Forwarding" 줄에서 URL 복사
예: https://abc123.ngrok-free.app
```

**3단계: TradingView Alert 업데이트 (URL이 바뀌었다면)**
```
TradingView → Alert → 편집
Webhook URL: https://새로운URL.ngrok-free.app/alert
저장!
```

**끝!** 이제 신호가 자동으로 들어옵니다 🎉

---

### 저녁에 PC 끌 때:

**아무것도 안 해도 됩니다!**
- 모든 창 닫기
- PC 끄기

다음날 다시 `start_all.bat` 실행하면 됩니다.

---

## 📊 신호 확인하는 방법

### 방법 1: Streamlit 대시보드 (추천!)

```
브라우저: http://localhost:8501

보이는 것:
✅ 최근 신호 목록 (표)
✅ 신호 차트 (그래프)
✅ Feature 분포
✅ 통계
```

### 방법 2: 데이터베이스 직접 확인

```powershell
cd C:\Users\ryanj\RYAION\vmsi-sdm
python -c "from server.db import SessionLocal, Signal; db = SessionLocal(); [print(f'{s.id}. {s.symbol} {s.signal} - {s.tf}') for s in db.query(Signal).all()]; db.close()"
```

**예상 출력:**
```
1. AAPL BUY - 1D
2. SPX BUY - 1D
3. SPX BUY - 1D
4. SPX BUY - 1D
```

---

## 🤖 학습 실행하는 방법

### 언제?
**신호가 10개 이상 모였을 때**

### 어떻게?

**수동 실행:**
```
폴더: C:\Users\ryanj\RYAION\vmsi-sdm
파일: run_learning.bat 더블클릭!
```

**실행 내용:**
1. 저장된 신호 읽기
2. 미래 수익률 계산 (자동)
3. Optuna로 최적 파라미터 찾기
4. 결과 저장: `presets/preset_B_candidate.json`

**소요 시간:** 5~30분 (trials 수에 따라)

**결과 파일:**
```
presets/preset_B_candidate.json

예시:
{
  "ema1_len": 20,
  "ema2_len": 50,
  "rsi_len": 14,
  "alpha": 0.85,
  "beta": 0.42,
  "gamma": 0.73,
  ...
}
```

---

## 🎯 학습 결과 적용하는 방법

### 1단계: preset_B_candidate.json 열기
```
파일: C:\Users\ryanj\RYAION\vmsi-sdm\presets\preset_B_candidate.json
메모장으로 열기
```

### 2단계: TradingView Indicator 설정 업데이트
```
TradingView 차트:
1. Indicator 우클릭 → "설정"
2. "파라미터 설정" 섹션
3. preset_B_candidate.json의 값들을 복사해서 입력
   - Alpha: 0.85
   - Beta: 0.42
   - Gamma: 0.73
   - ...
4. "확인" 클릭
```

### 3단계: 테스트
```
새 파라미터로 신호가 어떻게 바뀌는지 관찰
더 좋으면 계속 사용
안 좋으면 이전 설정으로 복귀
```

---

## 🔄 자주 묻는 질문 (FAQ)

### Q1: PC를 껐다가 다시 켜면?
**A:** `start_all.bat` 더블클릭 → ngrok URL 확인 → TradingView Alert 업데이트

### Q2: ngrok URL이 매번 바뀌는 게 불편해요
**A:** ngrok 유료 플랜 ($10/월) → 고정 URL 제공

### Q3: Streamlit Cloud 대시보드는 뭐예요?
**A:** 이전 클라우드 환경용. 지금은 안 씁니다. 로컬 Streamlit만 사용하세요.

### Q4: 신호가 안 들어와요
**A:** 체크리스트:
1. FastAPI 서버 실행 중? (검은 창 확인)
2. ngrok 실행 중? (http://localhost:4040 열림?)
3. TradingView Alert Webhook URL 최신인가?
4. Indicator가 차트에 추가되어 있나?

### Q5: 학습은 얼마나 자주 해야 하나요?
**A:** 
- 신호 10개: 첫 학습
- 신호 50개: 재학습 (더 정확함)
- 신호 100개 이상: 주 1회 재학습

### Q6: 데이터 백업은?
**A:** 
```
백업할 파일:
- vmsi_sdm.db (모든 신호)
- presets/*.json (학습 결과)

복사해서 안전한 곳에 보관!
```

---

## 🎓 실제 사용 시나리오

### 시나리오 1: 신호 수집 (1~2주)
```
목표: 신호 10개 이상 모으기

1일차:
- start_all.bat 실행
- TradingView Alert 설정
- 신호 대기

7일차:
- Streamlit에서 신호 확인 (예: 5개)
- 계속 대기

14일차:
- 신호 10개 모임!
- 다음 시나리오로
```

### 시나리오 2: 첫 학습 (14일차)
```
목표: 최적 파라미터 찾기

1. run_learning.bat 실행
2. 커피 한 잔 ☕ (20분 대기)
3. preset_B_candidate.json 생성됨
4. TradingView Indicator에 새 파라미터 적용
5. 백테스트로 성능 확인 (Strategy)
```

### 시나리오 3: 지속적 개선 (1개월 후)
```
목표: 더 많은 데이터로 재학습

신호 50개 모임:
1. run_learning.bat 재실행
2. 새 preset_B_candidate.json 확인
3. 이전 preset_A와 비교
4. 더 나은 것 선택
5. 계속 수집 → 재학습 반복
```

---

## 🚨 문제 해결

### FastAPI 서버가 안 켜져요
```
1. 검은 창(PowerShell)에서 에러 메시지 확인
2. 보통 원인: port 8000 이미 사용 중
3. 해결: taskkill /F /IM python.exe
4. 재시작: start_all.bat
```

### ngrok이 안 켜져요
```
1. ngrok.exe가 있나 확인:
   C:\Users\ryanj\RYAION\vmsi-sdm\ngrok.exe
2. 없으면: install_ngrok.bat 실행
3. authtoken 설정 확인
4. 재시작: start_ngrok.bat
```

### Streamlit이 안 켜져요
```
1. FastAPI가 먼저 켜져있어야 함
2. 포트 충돌 확인: taskkill /F /FI "WINDOWTITLE eq *streamlit*"
3. 수동 실행: streamlit run dashboard\app.py
```

---

## 💡 Pro Tips

### 1. ngrok URL 자동 확인
```bash
cd C:\Users\ryanj\RYAION\vmsi-sdm
.\check_ngrok_url.bat
```

### 2. 신호 빠르게 확인
```bash
python -c "from server.db import SessionLocal, Signal; print(f'Total: {SessionLocal().query(Signal).count()}')"
```

### 3. 전체 재시작 (문제 생기면)
```bash
.\restart_all.bat
```

### 4. 학습 강화 (더 정확하게)
```
run_learning.bat 수정:
--trials 200 → 500
--timeout 7200 → 14400
```

---

## 📁 중요 파일 위치

```
C:\Users\ryanj\RYAION\vmsi-sdm\
├── start_all.bat              ← 모든 서비스 시작
├── start_ngrok.bat            ← ngrok만 시작
├── run_learning.bat           ← 학습 실행
├── restart_all.bat            ← 전체 재시작
├── check_ngrok_url.bat        ← URL 확인
├── vmsi_sdm.db               ← 데이터베이스 (신호 저장소)
├── presets/
│   ├── preset_A_current.json  ← 현재 사용 중
│   └── preset_B_candidate.json ← 학습 결과 (최신)
└── pine/
    ├── indicator_sdm_v2.pine  ← TradingView Indicator
    └── strategy_sdm_v2.pine   ← TradingView Strategy
```

---

## 🎯 최종 요약

### 매일 할 일:
```
1. start_all.bat 실행 (1번 클릭)
2. ngrok URL 확인 (브라우저)
3. TradingView Alert 업데이트 (필요시)
```

### 일주일에 한 번:
```
1. Streamlit에서 신호 확인 (http://localhost:8501)
2. 신호 10개 이상이면 학습 실행 (run_learning.bat)
```

### 한 달에 한 번:
```
1. 학습 결과 적용 (preset → TradingView)
2. 백테스트로 성능 확인
3. 데이터 백업 (vmsi_sdm.db)
```

---

## 🎊 성공!

```
✅ 신호가 자동으로 들어옴
✅ 데이터베이스에 저장됨
✅ 학습으로 최적 파라미터 찾음
✅ TradingView에 적용
✅ 계속 개선됨!

비용: $0/월
시간: 하루 5분
결과: 데이터 기반 최적 매매!
```

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**대상**: 초보자도 쉽게 사용 가능

🎯 **이제 시작하세요!** `start_all.bat` 더블클릭! 🚀

