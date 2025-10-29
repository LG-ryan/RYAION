# VMSI-SDM 시스템 설계 문서

## 🏗️ 아키텍처 개요

VMSI-SDM은 **폐루프 자가학습 시스템**으로, 다음 4개의 주요 컴포넌트로 구성됩니다:

1. **TradingView 지표** (Pine Script v5)
2. **Webhook 서버** (FastAPI)
3. **학습 엔진** (Optuna)
4. **대시보드** (Streamlit)

---

## 📊 데이터 흐름

```
┌─────────────────────────────────────────────────────────┐
│                  TradingView Chart                      │
│                                                         │
│  Pine Script Indicator                                 │
│  ↓ Signal (BUY/SELL/WATCH)                            │
│  ↓ alert() with JSON payload                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ HTTP POST
                 ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Server                         │
│                                                         │
│  POST /alert → Validate → Store to DB                 │
│  ↓                                                      │
│  Background Task: Labeler                              │
│    ↓ Fetch OHLC from yfinance                         │
│    ↓ Calculate forward returns (3,5,10,20 bars)       │
│    ↓ Store labels to DB                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Periodic (manual/cron)
                 ↓
┌─────────────────────────────────────────────────────────┐
│                  Learner (Optuna)                       │
│                                                         │
│  1. Load signals + labels from DB                      │
│  2. Split: Train (70%) / Test (30%) - Walk Forward    │
│  3. Optimize parameters (Bayesian)                     │
│     - rsi_buy_th, vol_mult_buy, alpha, beta, ...      │
│  4. Evaluate on test set                               │
│  5. Save best params → preset_B_candidate.json         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Manual review
                 ↓
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard                    │
│                                                         │
│  - View signal timeline                                │
│  - Compare Preset A vs B                               │
│  - Visualize metrics (PF, MDD, Win Rate)              │
│  - Promote B → A (if better)                          │
│  - Copy Pine Script params                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ Copy-paste params
                 ↓
          [TradingView Indicator]  ← Loop back
```

---

## 🗄️ 데이터베이스 스키마

### Tables

#### 1. `signals`

| Column        | Type     | Description                      |
|---------------|----------|----------------------------------|
| id            | Integer  | Primary Key                      |
| ts            | String   | TradingView timestamp (ms)       |
| symbol        | String   | Symbol (AAPL, BTCUSD, ...)       |
| tf            | String   | Timeframe (5, 1D, ...)           |
| signal        | String   | BUY, SELL, WATCH_UP, WATCH_DOWN  |
| features_json | JSON     | TrendScore, Prob, RSI, ...       |
| params_json   | JSON     | alpha, beta, gamma, ...          |
| bar_o/h/l/c   | Float    | OHLC (filled by labeler)         |
| created_at    | DateTime | Creation timestamp               |

#### 2. `labels`

| Column     | Type     | Description                     |
|------------|----------|---------------------------------|
| id         | Integer  | Primary Key                     |
| signal_id  | Integer  | Foreign Key → signals.id        |
| fwd_n      | Integer  | Forward N bars (3, 5, 10, 20)   |
| fwd_ret    | Float    | Forward return                  |
| broke_high | Boolean  | High breakout (>+3%)            |
| broke_low  | Boolean  | Low breakdown (>-3%)            |
| created_at | DateTime | Creation timestamp              |

#### 3. `experiments`

| Column     | Type     | Description                     |
|------------|----------|---------------------------------|
| id         | Integer  | Primary Key                     |
| run_id     | String   | Unique run identifier           |
| params     | JSON     | Optimized parameters            |
| metrics    | JSON     | PF, MDD, Win Rate, PSU, ...     |
| created_at | DateTime | Creation timestamp              |

#### 4. `reports`

| Column        | Type     | Description                     |
|---------------|----------|---------------------------------|
| id            | Integer  | Primary Key                     |
| experiment_id | Integer  | Foreign Key → experiments.id    |
| path          | String   | Report file path                |
| notes         | Text     | Additional notes                |
| created_at    | DateTime | Creation timestamp              |

---

## 🧠 학습 알고리즘

### Optuna Bayesian Optimization

**목표**: 파라미터 공간에서 최적 조합 찾기

**최적화 대상 파라미터**:
- `rsi_buy_th` (50~70)
- `rsi_sell_th` (30~50)
- `vol_mult_buy` (1.0~3.0)
- `vol_mult_sell` (1.0~3.0)
- `vcp_ratio_th` (0.1~0.8)
- `dist_ath_max` (0.05~0.3)
- `alpha`, `beta`, `gamma`, `delta`, `epsilon` (가중치)
- `hysteresis_len` (2~5)
- `cooldown_bars` (2~5)
- `vix_w`, `dxy_w`, `us10y_w`, `hygief_w` (매크로 가중치)

**목적 함수**:
```python
score = (
    pf * 0.4 +                # Profit Factor
    (1 - mdd) * 0.2 +         # Max Drawdown (inverted)
    psu_10 * 0.3 +            # PSU 10-bar accuracy
    win_rate * 0.1            # Win Rate
)
```

**검증 방식**:
- **Walk Forward**: Train (70%) → Test (30%)
- 시간순 분할로 미래 데이터 누수 방지

---

## 🎨 Pine Script 지표 로직

### Stage 판단

```
TrendScore = (
    alpha * (EMA20 > EMA50) +
    beta * (RSI / 100) +
    gamma * (VolMult / 3) +
    delta * (1 - VCP_ratio)
) * 100

Prob = (TrendScore / 100 + epsilon * MacroScore) / (1 + epsilon)

Stage:
  - BUY: TrendScore >= 70 AND Prob >= 0.6 AND RSI > rsi_buy_th AND VolMult > vol_mult_buy
  - SELL: TrendScore <= 30 AND Prob <= 0.4 AND RSI < rsi_sell_th AND VolMult > vol_mult_sell
  - WATCH_UP: TrendScore > 50 AND Prob > 0.5
  - WATCH_DOWN: TrendScore < 50 AND Prob < 0.5
```

### 리페인트 방지

- 모든 계산은 `barstate.isconfirmed` (확정봉) 기준
- Hysteresis: 최근 3봉 평균 사용
- Cooldown: 신호 발생 후 3봉 동안 재신호 차단

---

## 📈 성능 지표

### 1. Profit Factor (PF)

```
PF = sum(positive returns) / abs(sum(negative returns))
```

**목표**: PF > 1.5

### 2. Max Drawdown (MDD)

```
MDD = max((cumulative - running_max) / running_max)
```

**목표**: MDD < 0.2 (20%)

### 3. Win Rate

```
Win Rate = count(returns > 0) / count(all returns)
```

**목표**: Win Rate > 0.6

### 4. PSU (Position Setup Utility)

신호 정확도. N봉 후 목표 수익률 달성 비율.

**목표**: PSU 10-bar > 0.65

### 5. Sharpe Ratio

```
Sharpe = sqrt(252) * mean(excess_returns) / std(returns)
```

---

## 🔒 보안 고려사항

### 1. Webhook 검증

- API Secret 사용 (환경변수)
- IP 화이트리스트

### 2. 데이터베이스

- 로컬: SQLite (개발)
- 프로덕션: PostgreSQL with SSL
- 패스워드는 환경변수로 관리

### 3. CORS

- Streamlit과 FastAPI 간 통신 허용
- 프로덕션에서는 특정 도메인만 허용

---

## 🚀 확장 가능성

### 1. 멀티 심볼/타임프레임 지원

- 현재: 단일 지표 → 여러 심볼에서 신호 수신
- 확장: 심볼/타임프레임별 개별 프리셋 관리

### 2. 실시간 자동 매매

- 신호 수신 → Binance/Bybit API 연동
- 리스크 관리 모듈 추가

### 3. 앙상블 학습

- 여러 모델의 예측 결합
- XGBoost, LightGBM 등 추가

### 4. 매크로 지표 자동 수집

- VIX, DXY, US10Y, HYG/IEF 실시간 수집
- request.security() 활용

---

## 📊 모니터링 & 로깅

### 로그 레벨

- `DEBUG`: 개발 중 상세 로그
- `INFO`: 신호 수신, 라벨 생성 등
- `WARNING`: 데이터 누락, 네트워크 지연
- `ERROR`: DB 오류, API 실패

### 메트릭 추적

- 신호 수신률 (signals/hour)
- 라벨 생성 성공률
- 최적화 실행 시간
- 대시보드 접속 수

---

## 🧪 테스트 전략

### 1. 단위 테스트

- 각 모듈별 독립 테스트
- pytest 사용

### 2. 통합 테스트

- 서버 → DB → Labeler → Learner 전체 파이프라인

### 3. 백테스트

- Pine Strategy로 과거 데이터 검증
- Out-of-sample 기간 성능 확인

---

## 🔄 배포 전략

### 1. 로컬 개발

```bash
python server/app.py  # 개발 서버
streamlit run dashboard/app.py  # 대시보드
```

### 2. Docker 배포

```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 클라우드 배포

- AWS EC2 / Azure VM
- PostgreSQL RDS
- nginx 리버스 프록시
- SSL 인증서 (Let's Encrypt)

---

**이 설계 문서는 VMSI-SDM의 전체 아키텍처를 설명합니다. 구현 세부사항은 코드 주석 및 API.md를 참조하세요.**

