# 🚀 VMSI-SDM 프로젝트

**Volde Momentum Stage Indicator - Stage Detection Model**

자가학습형 TradingView 지표 시스템

---

## 📦 프로젝트 구조

```
vmsi-sdm/
├── pine/                           # TradingView Pine Script
│   ├── indicator_sdm_v2.pine      # 지표 (신호 생성 + Webhook)
│   └── strategy_sdm_v2.pine       # 전략 (백테스트용)
├── server/                         # FastAPI Webhook 서버
│   ├── app.py                     # 메인 서버
│   ├── schemas.py                 # Pydantic 스키마
│   ├── db.py                      # 데이터베이스 모델
│   └── labeler.py                 # 미래 수익률 라벨러
├── learner/                        # Optuna 학습 엔진
│   ├── data.py                    # 데이터 로더
│   ├── metrics.py                 # 성능 지표
│   ├── tune.py                    # 파라미터 최적화
│   ├── preset.py                  # 프리셋 관리
│   └── ablation.py                # Ablation 분석
├── dashboard/                      # Streamlit 대시보드
│   └── app.py                     # 실시간 모니터링 UI
├── presets/                        # 프리셋 JSON
│   ├── preset_A_current.json      # 현재 프리셋
│   └── preset_B_candidate.json    # 후보 프리셋
├── docs/                           # 문서
│   ├── README.md                  # 사용 가이드
│   ├── DESIGN.md                  # 시스템 설계
│   └── API.md                     # API 명세
├── init_project.py                 # 초기화 스크립트
├── requirements.txt                # 패키지 의존성
└── env.example                     # 환경변수 예시
```

---

## 🎯 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
# .env 파일 생성
copy env.example .env

# 필요시 DATABASE_URL 등 수정
```

### 3. 초기화

```bash
python init_project.py
```

### 4. 서버 실행

**Webhook 서버:**
```bash
python server/app.py
```

**대시보드:**
```bash
streamlit run dashboard/app.py
```

### 5. TradingView 연결

1. `pine/indicator_sdm_v2.pine` 복사
2. TradingView Pine Editor에 붙여넣기
3. Alert 생성 → Webhook URL: `http://your-ip:8000/alert`

---

## 📚 문서 읽기 순서

### 시작 가이드 (루트 폴더)
1. **00_QUICKSTART.md** ← 가장 먼저! 빠른 시작
2. **01_QUICK_FIX.md** ← 문제 발생 시 즉시 해결
3. **02_DEPLOY_CHECKLIST.md** ← 클라우드 배포 (내일 할 것)

### 상세 문서 (docs 폴더)
1. **docs/01_README.md** ← 프로젝트 사용법
2. **docs/02_DESIGN.md** ← 시스템 아키텍처
3. **docs/03_API.md** ← Webhook API 명세
4. **docs/04_TRADINGVIEW_SETUP.md** ← TradingView 연결 방법
5. **docs/05_CLOUD_DEPLOYMENT.md** ← 무료 클라우드 배포 (24/7)

---

## 🛠️ 주요 명령어

```bash
# DB 초기화
python -c "from server.db import init_db; init_db()"

# 라벨 생성
curl -X POST http://localhost:8000/labels/generate

# 파라미터 최적화
python learner/tune.py BUY 50

# Ablation 분석
python learner/ablation.py
```

---

**VMSI-SDM v2.0 | 자가학습형 트레이딩 시스템**

