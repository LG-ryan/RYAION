# VMSI-SDM: 자가학습형 TradingView 지표 시스템

**Volde Momentum Stage Indicator - Stage Detection Model**

## 🎯 프로젝트 개요

VMSI-SDM은 TradingView 지표가 실시간으로 신호를 생성하고, 그 신호의 결과를 자동으로 학습하여 파라미터를 최적화하는 **자가진화형 트레이딩 시스템**입니다.

### 핵심 특징

- ✅ **TradingView 네이티브**: Pine Script v5 기반 지표/전략
- ✅ **자가학습**: Optuna Bayesian Optimization으로 파라미터 자동 튜닝
- ✅ **투명성**: Streamlit 대시보드로 학습 과정 시각화
- ✅ **워크포워드 검증**: 과거 학습, 최근 검증 방식
- ✅ **리페인트 방지**: 확정봉 기준 신호 생성

---

## 🚀 5분 안에 시작하기

### 1. 환경 설정

```bash
# 레포지토리 이동
cd vmsi-sdm

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp env.example .env
# .env 파일을 열어서 필요한 설정 수정
```

### 2. 데이터베이스 초기화

```bash
# DB 초기화
python -c "from server.db import init_db; init_db()"
```

### 3. Webhook 서버 실행

```bash
# FastAPI 서버 시작
python server/app.py

# 또는
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 `http://localhost:8000` 에서 접속 가능합니다.

### 4. TradingView 지표 설정

1. TradingView에서 Pine Script 에디터 열기
2. `pine/indicator_sdm_v2.pine` 내용 복사-붙여넣기
3. 차트에 추가
4. **Alert 생성**:
   - Condition: `VMSI-SDM v2`
   - Message: (기본 JSON 페이로드 사용)
   - Webhook URL: `http://your-server-ip:8000/alert`

### 5. Streamlit 대시보드 실행

```bash
streamlit run dashboard/app.py
```

대시보드: `http://localhost:8501`

---

## 📊 시스템 구조

```
TradingView 지표 (Pine v5)
    ↓ Webhook
FastAPI 서버 (신호 수신 & DB 저장)
    ↓
Labeler (미래 수익률 계산)
    ↓
Learner (Optuna 파라미터 최적화)
    ↓
Preset JSON 생성
    ↓
Streamlit 대시보드 (A/B 비교)
    ↓
사용자 승인 → TradingView 지표 업데이트
```

---

## 🔄 학습 사이클 실행

### 자동 라벨링

```bash
# 최근 30일 신호에 대해 라벨 생성
python -c "from server.labeler import label_recent_signals; from server.db import SessionLocal; db=SessionLocal(); label_recent_signals(db, 30); db.close()"
```

### 파라미터 최적화

```bash
# BUY 신호 최적화 (50 trials)
python learner/tune.py BUY 50

# SELL 신호 최적화
python learner/tune.py SELL 50
```

### Ablation Study

```bash
# 피처 중요도 분석
python learner/ablation.py
```

결과는 `docs/ablation_report.md`에 저장됩니다.

---

## 📁 디렉토리 구조

```
vmsi-sdm/
├── pine/                    # TradingView Pine Script
│   ├── indicator_sdm_v2.pine   # 지표
│   └── strategy_sdm_v2.pine    # 전략 (백테스트용)
├── server/                  # FastAPI 서버
│   ├── app.py                  # 메인 서버
│   ├── schemas.py              # Pydantic 스키마
│   ├── db.py                   # SQLAlchemy 모델
│   └── labeler.py              # 라벨러
├── learner/                 # 학습 모듈
│   ├── data.py                 # 데이터 로더
│   ├── metrics.py              # 성능 지표
│   ├── tune.py                 # Optuna 튜너
│   ├── preset.py               # 프리셋 관리
│   └── ablation.py             # Ablation 분석
├── dashboard/               # Streamlit 대시보드
│   └── app.py
├── presets/                 # 프리셋 JSON
│   ├── preset_A_current.json   # 현재 프리셋
│   └── preset_B_candidate.json # 후보 프리셋
├── docs/                    # 문서
│   ├── README.md               # 이 파일
│   ├── DESIGN.md               # 아키텍처 설계
│   └── API.md                  # API 명세
├── requirements.txt         # 패키지 의존성
└── env.example              # 환경변수 예시
```

---

## 🧪 테스트

### End-to-End 테스트

```bash
# 1. 서버 실행
python server/app.py &

# 2. 가짜 알럿 전송
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -d @test_alert.json

# 3. 신호 확인
curl http://localhost:8000/signals?limit=5

# 4. 라벨 생성
curl -X POST http://localhost:8000/labels/generate?limit=10
```

---

## 📖 주요 사용 사례

### 1. 새로운 프리셋 적용하기

1. Learner로 최적화 실행 → `preset_B_candidate.json` 생성
2. Streamlit 대시보드에서 A/B 비교
3. 성능이 우수하면 "승격" 버튼 클릭 → `preset_A_current.json` 업데이트
4. 대시보드에서 Pine Script 코드 복사
5. TradingView 지표에 붙여넣기

### 2. 특정 심볼/타임프레임 분석

```python
from server.db import SessionLocal, Signal
from learner.data import DataLoader

db = SessionLocal()
loader = DataLoader(db)
df = loader.load_signals_with_labels()

# AAPL 1D만 필터링
df_aapl = df[(df['symbol'] == 'AAPL') & (df['tf'] == '1D')]

# 성능 분석
from learner.metrics import PerformanceMetrics
metrics = PerformanceMetrics.calculate_all_metrics(df_aapl, 'BUY')
print(metrics)
```

---

## ⚙️ 고급 설정

### PostgreSQL 사용 (프로덕션)

`.env` 파일:
```
DATABASE_URL=postgresql://user:password@localhost:5432/vmsi_sdm
```

### Webhook 보안

`.env` 파일:
```
WEBHOOK_SECRET=your_secret_key
```

서버에서 검증 추가:
```python
from fastapi import Header, HTTPException

@app.post("/alert")
async def receive_alert(alert: TradingViewAlert, x_webhook_secret: str = Header(None)):
    if x_webhook_secret != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(401, "Unauthorized")
    # ...
```

---

## 🐛 문제 해결

### 1. 서버가 신호를 받지 못해요

- TradingView Alert Webhook URL 확인
- 서버 방화벽 설정 확인
- ngrok 등으로 로컬 서버 외부 노출

### 2. 라벨이 생성되지 않아요

- yfinance 데이터가 정상인지 확인
- 심볼 이름이 yfinance 형식과 일치하는지 확인 (예: BTCUSD → BTC-USD)

### 3. Optuna 최적화가 너무 느려요

- `n_trials` 줄이기
- `timeout` 설정
- 데이터 기간 줄이기

---

## 📚 참고 자료

- [Pine Script v5 문서](https://www.tradingview.com/pine-script-docs/v5/)
- [Optuna 문서](https://optuna.readthedocs.io/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Streamlit 문서](https://docs.streamlit.io/)

---

## 📝 라이선스

MIT License

---

## 👥 기여

이슈 및 PR 환영합니다!

---

**🚀 VMSI-SDM으로 자가학습형 트레이딩 시스템을 경험하세요!**

