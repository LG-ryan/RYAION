# VMSI-SDM 자가학습형 트레이딩뷰 지표 시스템 (Volde Momentum Stage Indicator - Stage Detection Model)

## 🧭 시스템 역할
너는 “VMSI-SDM” 프로젝트의 **리드 엔지니어 에이전트**이다.  
목표는 **TradingView 지표(Pine v5)** 와 **Webhook 서버 + 학습 루프 + 시각화 대시보드**를 하나로 연결하여  
“지표가 스스로 학습하고, 사용자가 그 과정을 보고 배우며, 개선 결과를 다시 반영하는 완전 자율 학습 시스템”을 만드는 것이다.  
지표 실행 플랫폼은 반드시 **TradingView** 이어야 하며, 다른 차트 플랫폼은 허용되지 않는다.  
모든 코드는 하나의 레포지토리 안에서 명확히 구조화되어야 한다.

---

## 📁 프로젝트 디렉토리 구조
```
vmsi-sdm/
  pine/
    indicator_sdm_v2.pine
    strategy_sdm_v2.pine
  server/
    app.py
    schemas.py
    db.py
    labeler.py
  learner/
    data.py
    tune.py
    metrics.py
    preset.py
    ablation.py
  dashboard/
    app.py
  presets/
    preset_A_current.json
    preset_B_candidate.json
  docs/
    README.md
    DESIGN.md
    API.md
  .env.example
  requirements.txt
```

---

## 🧩 기능 개요

### 1. TradingView 지표 (Pine v5)
- 신호: `BUY`, `SELL`, `WATCH_UP`, `WATCH_DOWN`  
- Stage 배경색 및 패널 표시 (Stage, Dir, TrendScore, Prob, MacroFlag)  
- 모든 신호는 **확정봉 기준**으로 계산하며 **리페인트 방지**.  
- 신호 발생 시 `alert()`로 아래 JSON 포맷의 페이로드를 Webhook으로 전송:
```json
{
  "symbol":"{{ticker}}","tf":"{{interval}}","t":"{{time}}",
  "signal":"BUY|WATCH_UP|WATCH_DOWN|SELL",
  "features":{
    "trendScore":78,"prob":0.63,
    "ema20_above_50":true,"rsi":58.2,"vol_mult":1.7,
    "vcp_ratio":0.54,"dist_ath":0.06,
    "macro":{"vix":18.4,"dxy_trend":"down","us10y_trend":"flat","hyg_ief":"bull"}
  },
  "params":{"ema1":20,"ema2":50,"rsi":14,"vcp":20,"alpha":0.8,"beta":0.35,"gamma":0.7,"delta":0.6,"epsilon":0.8}
}
```
- 히스테리시스(최근 3봉 평균)와 쿨다운(3봉) 적용으로 신호 잦은 변경 방지.

---

### 2. Webhook 서버 (FastAPI)
- 엔드포인트: `POST /alert`
- TradingView에서 전송된 JSON 데이터를 검증 후 데이터베이스에 저장.  
- 수신 시 OHLC 보강 및 파생 피처 자동 생성.  
- 테이블 구조:
  - `signals(id, ts, symbol, tf, signal, features_json, params_json, bar_o, bar_h, bar_l, bar_c)`
  - `labels(signal_id, fwd_n, fwd_ret, broke_high, broke_low)`
  - `experiments(run_id, params, metrics, created_at)`
  - `reports(run_id, path, notes)`
- DB는 로컬에서 SQLite, 배포 시 PostgreSQL 사용 (`DATABASE_URL` 환경변수로 제어).

---

### 3. 라벨러 (Labeler)
- 신호 발생 후 `3, 5, 10, 20봉` 뒤의 결과를 계산:
  - `future_return_N`, `break_high_N`, `break_low_N`  
- 백엔드에서 Yahoo Finance 혹은 Polygon 데이터를 이용해 과거 시세 보강.

---

### 4. 학습기 (Learner)
- **Optuna 기반 Bayesian Optimization**으로 파라미터 튜닝.
- 최적화 대상 파라미터:
  - `rsi_buy_th`, `rsi_sell_th`, `vol_mult_buy`, `vcp_ratio_th`, `dist_ath_max`
  - `macro_weights = {vix_w, dxy_w, us10y_w, hygief_w}`
  - `hysteresis_len`, `cooldown_bars`, `prob_window`
- 평가 목표:
  - 리드타임 성공률(PSU/PSD 정확도)
  - Profit Factor (PF)
  - Max Drawdown
  - 파라미터 ±20% 변동 시 성능 안정성
- **워크포워드 검증** 방식 사용 (과거 구간 학습, 최근 구간 검증).
- 산출물:
  - `preset_B_candidate.json`  
  - `docs/report_YYYYMMDD.md` (튜닝 결과 리포트)

---

### 5. 대시보드 (Streamlit)
- 실시간 신호 타임라인 및 실제 성과 시각화.  
- A/B 비교: 현재 프리셋 vs 새 프리셋.  
- 매크로 변수별 영향도(Ablation) 차트 표시.  
- “이번 신호가 왜 나왔는가”를 피처 기여도(TrendScore, VolMult, RSI 등)로 텍스트 설명.  
- 버튼 클릭으로 새 프리셋 JSON을 복사 가능 (`// @preset vYYYYMMDD`).

---

### 6. 프리셋 관리
- 매 학습 사이클마다 새로운 후보 프리셋(B) 생성.  
- 대시보드에서 B와 A 비교 후 수동 승인 시 `preset_A_current.json`으로 갱신.  
- 프리셋 예시:
```json
{
  "version":"v2025-10-29",
  "params":{
    "ema1":20,"ema2":50,"rsi":14,"vcp":20,
    "rsi_buy_th":55,"rsi_sell_th":45,
    "vol_mult_buy":1.5,"vol_mult_sell":1.3,
    "macro_weights":{"vix_w":-0.3,"dxy_w":-0.2,"us10y_w":-0.2,"hygief_w":0.4},
    "alpha":0.8,"beta":0.35,"gamma":0.7,"delta":0.6,"epsilon":0.8,
    "hysteresis_len":3,"cooldown_bars":3
  },
  "metrics":{"pf":1.47,"mdd":0.14,"psu_success":0.68,"psd_success":0.62}
}
```

---

### 7. 필수 패키지 (requirements.txt)
```
fastapi
uvicorn
sqlalchemy
pandas
numpy
optuna
yfinance
streamlit
pydantic
python-dotenv
matplotlib
scikit-learn
```

---

### 8. 개발 순서
1. `server/app.py` 구현 및 Webhook 수신 테스트  
2. `labeler.py` 추가 및 미래 라벨 계산  
3. `learner/data.py`, `tune.py`, `metrics.py` 작성  
4. `preset_B_candidate.json` 생성 및 성능 리포트 산출  
5. `dashboard/app.py` 제작하여 실험 결과 시각화  
6. `pine/indicator_sdm_v2.pine` 템플릿에 프리셋 주입 포인트 추가  
7. `docs/`에 설치 및 사용 가이드 작성

---

### 9. 테스트 / 검증
- 예시 종목: AAPL, QQQ, NVDA, BTCUSD  
- 가짜 alert 데이터로 end-to-end 검증  
- 서버 → DB → 라벨러 → 튜너 → 리포트 → 대시보드까지 전 과정 점검  
- 누락 데이터 없는지, 결과 일관성 확인

---

### 10. 문서 구성
- `README.md`: 5분 안에 시작하기 (TradingView 연결~대시보드 확인)  
- `DESIGN.md`: 데이터 흐름 및 아키텍처 설명  
- `API.md`: Webhook 규격 및 예시 페이로드  
- `report_YYYYMMDD.md`: 실험 결과 자동 저장  

---

### 11. 코드 품질 기준
- Black / Ruff 포맷팅  
- 타입힌트 필수  
- Google-style Docstring  
- 모듈 간 순환 참조 금지  
- 예외 처리 명확히  
- 하드코딩 대신 프리셋 JSON 기반 파라미터 주입

---

### 12. 전체 동작 흐름
1. TradingView 지표가 신호 발생 → Webhook으로 전송  
2. 서버가 신호 및 피처를 DB에 저장  
3. Learner가 주기적으로 DB 분석 → 새로운 파라미터 최적화  
4. Streamlit 대시보드에서 성능/비교 시각화  
5. 사용자가 결과를 확인하고 프리셋 적용  
6. TradingView 지표가 새 파라미터로 작동  
→ 완전 자율 학습 순환 루프 완성

---

### 13. 산출물
- 즉시 실행 가능한 코드 레포  
- 예시 `.env` 파일  
- 샘플 데이터 및 초기 테스트 리포트  
- 문서 완비, 명확한 커밋 로그 및 단계별 설명

---

### 14. 실행 단계
1. 이 문서를 `VMSI-SDM_INIT.md` 로 저장  
2. Cursor 또는 Codex에서 이 파일 내용을 그대로 붙여넣어 실행  
3. 코드 생성 및 각 단계별 사용법 출력  
4. `uvicorn server.app:app --reload` 로 서버 실행  
5. `streamlit run dashboard/app.py` 로 대시보드 실행  
6. TradingView 알럿 Webhook 연결 후 실제 데이터 수집 시작

---

### 15. 초기 출력 메시지 예시
```
🚀 프로젝트 초기화 완료: VMSI-SDM
모듈: server ✓ learner ✓ dashboard ✓ pine ✓
다음 단계: Webhook POST /alert 테스트
```

---

### 16. 필수 원칙
- **TradingView 전용** (Pine v5 확정봉 기반)  
- **투명한 학습 과정**: 매 사이클마다 인간이 이해 가능한 피드백 리포트 제공  
- **자가 진화 구조**: 튜닝 결과가 다시 Pine 지표로 피드백  
- **교육형 시스템**: 사용자가 학습 루프를 직접 시각적으로 이해하고 개선 가능해야 함  
