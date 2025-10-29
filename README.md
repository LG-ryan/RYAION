# 🚀 VMSI-SDM v2.1

**Volde Momentum Stage Indicator - Self-Learning Detection Model**

자가학습형 Stage Detection 시스템 (100% 무료, 로컬 환경)

---

## 📊 시스템 개요

```
TradingView Indicator (Pine Script v6)
    ↓ Webhook (ngrok)
로컬 FastAPI 서버 (SQLite)
    ↓
Optuna 학습 (무제한!)
    ↓
최적 파라미터 → Indicator 적용
```

---

## ✨ 주요 기능

### 🎯 Stage Detection
- **BUY/SELL/WATCH** 신호 자동 감지
- EMA, RSI, Volume, VCP 복합 분석
- Hysteresis & Cooldown (노이즈 제거)
- 실시간 매크로 데이터 통합 (선택)

### 🤖 Optuna 자동 학습
- 베이지안 최적화 (무제한 trials)
- Work-forward validation
- Preset 자동 생성 및 적용

### 📈 Streamlit 대시보드
- 실시간 신호 모니터링
- Feature 분포 시각화
- 학습 결과 분석

---

## 💰 비용

**완전 무료 ($0/월)**
- ngrok Free: 2시간 세션 (재시작 필요)
- 로컬 SQLite: 무제한 저장
- 로컬 학습: 무제한 trials

**선택적 유료 ($10/월)**
- ngrok Paid: 고정 URL, 무제한 세션

---

## 🚀 빠른 시작

### 1. 설치
```bash
cd C:\Users\ryanj\RYAION\vmsi-sdm
pip install -r requirements.txt
```

### 2. ngrok 설정
```bash
# ngrok 다운로드: https://ngrok.com/
# ngrok.exe를 vmsi-sdm 폴더에 복사
.\ngrok.exe config add-authtoken YOUR_TOKEN
```

### 3. 시작
```bash
.\start_all.bat
```

**실행되는 것들**:
- FastAPI 서버 (port 8000)
- ngrok 터널 (public URL)
- Streamlit 대시보드 (port 8501)

### 4. TradingView Alert 설정
```
1. http://localhost:4040에서 ngrok URL 복사
2. TradingView → Alert 생성
3. Webhook URL: https://abc123.ngrok-free.app/webhook/tv
```

---

## 📚 문서

### 시작하기
- `01_START_HERE.md` - 프로젝트 개요
- `02_QUICKSTART.md` - 빠른 시작 가이드
- `05_DEPLOY_CHECKLIST.md` - 배포 체크리스트

### 설정 가이드
- `08_NGROK_LOCAL_SETUP.md` - ngrok + 로컬 완전 가이드 ⭐
- `07_TRADINGVIEW_ALERT_SETUP.md` - Alert 설정

### 기술 문서
- `06_REFACTOR_SUMMARY.md` - Pine Script v2.1 리팩토링
- `03_STAGE_DETECTION_RESTORE.md` - Stage Detection 철학
- `docs/01_README.md` - 시스템 아키텍처
- `docs/02_DESIGN.md` - 설계 문서
- `docs/03_API.md` - API 명세

---

## 🎯 일일 루틴

### 트레이딩 시작
```bash
1. start_all.bat 실행
2. ngrok URL 확인 (http://localhost:4040)
3. TradingView Alert 업데이트 (첫 실행 시)
```

### 2시간마다
```bash
ngrok 재시작 + TradingView Alert URL 업데이트 (30초)
```

### 학습 (자동)
```
Windows Task Scheduler → 매일 새벽 2시 자동 실행
또는 수동: .\run_learning.bat
```

---

## 📊 성능

### 로컬 vs 클라우드
```
┌─────────────────┬────────┬─────────┐
│                 │ 로컬    │ 클라우드 │
├─────────────────┼────────┼─────────┤
│ 비용            │ $0     │ $7~10   │
│ 학습 trials     │ 무제한  │ 50~100  │
│ 속도            │ 빠름    │ 느림     │
│ 데이터 제어     │ 완전    │ 제한적   │
└─────────────────┴────────┴─────────┘
```

---

## 🛠️ 기술 스택

- **Indicator**: Pine Script v6
- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite
- **Learning**: Optuna (Bayesian Optimization)
- **Dashboard**: Streamlit + Plotly
- **Tunnel**: ngrok

---

## 📁 프로젝트 구조

```
vmsi-sdm/
├── pine/                    # TradingView Pine Scripts
│   ├── indicator_sdm_v2.pine   # 지표 (v2.1)
│   └── strategy_sdm_v2.pine    # 전략 (백테스트용)
│
├── server/                  # FastAPI 서버
│   ├── app.py                  # 메인 서버
│   ├── db.py                   # 데이터베이스 모델
│   ├── schemas.py              # Pydantic 스키마
│   └── labeler.py              # 미래 수익률 계산
│
├── learner/                 # Optuna 학습
│   ├── tune.py                 # 최적화 루프
│   ├── data.py                 # 데이터 로더
│   ├── metrics.py              # 백테스트 엔진
│   └── preset.py               # Preset 관리
│
├── dashboard/               # Streamlit 대시보드
│   └── app.py                  # 대시보드 앱
│
├── presets/                 # 학습 결과
│   ├── preset_A_current.json   # 현재 파라미터
│   └── preset_B_candidate.json # 학습된 파라미터
│
├── start_all.bat            # 통합 시작
├── start_ngrok.bat          # ngrok 시작
├── check_ngrok_url.bat      # URL 확인
├── run_learning.bat         # 학습 실행
├── vmsi_sdm.db             # SQLite DB
└── ngrok.exe               # ngrok 실행 파일
```

---

## 🔧 트러블슈팅

### FastAPI 시작 안 됨
```bash
taskkill /f /im uvicorn.exe
start_server.bat
```

### ngrok 세션 만료
```bash
start_ngrok.bat
# 새 URL 복사 → TradingView Alert 업데이트
```

### SQLite 오류
```bash
vmsi_sdm.db 삭제
python -c "from server.db import init_db; init_db()"
```

---

## 💡 Pro Tips

### ngrok 유료 플랜 ($10/월)
- 고정 URL (Alert 수정 불필요)
- 무제한 세션
- 편의성 대폭 향상

### 학습 강화
```bash
# run_learning.bat 수정
--trials 500  # 더 많은 시도
--timeout 14400  # 더 긴 시간
```

### 백업
```bash
# 정기적 백업
vmsi_sdm.db
presets/*.json
```

---

## 📈 Stage Detection 철학

**목적**: "며칠 전 신호" 감지 (스윙 트레이딩)

**신호 빈도**:
- Fast Mode OFF: 주~월 단위 (보수적, 안정적) ← **추천**
- Fast Mode ON: 일~주 단위 (빠르지만 노이즈)

**권장 설정**:
- 타임프레임: 1D (일봉)
- Hysteresis: 5
- Cooldown: 10

---

## 🎉 완료!

```
✅ 100% 무료
✅ 무제한 학습
✅ 빠른 속도
✅ 완전한 제어
```

**비용**: $0/월  
**성능**: 클라우드보다 우수  
**제어**: 100% 자유  

---

**License**: MIT  
**Author**: Ryan (with Cursor AI)  
**Version**: v2.1  
**Date**: 2025-10-29  

🏠 **로컬 최고! PC에서 모든 것을!**
