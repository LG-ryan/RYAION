# 🚀 VMSI-SDM 빠른 시작 가이드

## 📋 사전 요구사항

- **Python 3.9 이상** 필수
- pip 패키지 매니저

---

## ⚡ 1분 안에 시작하기

### Windows

```powershell
# 1. 가상환경 생성 (권장)
python -m venv venv
.\venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 파일 생성
copy env.example .env

# 4. 데이터베이스 초기화
python -c "from server.db import init_db; init_db()"

# 5. 서버 실행
python server\app.py
```

### Linux/Mac

```bash
# 1. 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 파일 생성
cp env.example .env

# 4. 데이터베이스 초기화
python -c "from server.db import init_db; init_db()"

# 5. 서버 실행
python server/app.py
```

---

## 🎯 단계별 실행

### Step 1: Webhook 서버 실행

**터미널 1:**
```bash
python server/app.py
```

서버가 실행되면:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Step 2: 대시보드 실행

**터미널 2:**
```bash
streamlit run dashboard/app.py
```

대시보드가 실행되면:
- Dashboard: http://localhost:8501

### Step 3: TradingView 지표 설정

1. TradingView 열기
2. Pine Editor 열기
3. `pine/indicator_sdm_v2.pine` 내용 복사
4. Pine Editor에 붙여넣기
5. "Save" → "Add to Chart"
6. Alert 생성:
   - Condition: "VMSI-SDM v2"
   - Webhook URL: `http://your-server-ip:8000/alert`
   - Message: (자동 생성됨)

---

## 🧪 테스트

### 1. 서버 Health Check

```bash
curl http://localhost:8000/
```

예상 출력:
```json
{
  "status": "running",
  "service": "VMSI-SDM Webhook Server",
  "version": "2.0.0"
}
```

### 2. 테스트 신호 전송

`test_alert.json` 파일 생성:
```json
{
  "symbol": "AAPL",
  "tf": "1D",
  "t": "1698624000000",
  "signal": "BUY",
  "features": {
    "trendScore": 78.5,
    "prob": 0.68,
    "ema20_above_50": true,
    "rsi": 58.2,
    "vol_mult": 1.7,
    "vcp_ratio": 0.54,
    "dist_ath": 0.06,
    "macro": {
      "vix": 18.4,
      "dxy_trend": "down",
      "us10y_trend": "flat",
      "hyg_ief": "bull"
    }
  },
  "params": {
    "ema1": 20,
    "ema2": 50,
    "rsi": 14,
    "vcp": 20,
    "alpha": 0.8,
    "beta": 0.35,
    "gamma": 0.7,
    "delta": 0.6,
    "epsilon": 0.8
  }
}
```

전송:
```bash
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -d @test_alert.json
```

### 3. 신호 조회

```bash
curl http://localhost:8000/signals?limit=5
```

### 4. 통계 확인

```bash
curl http://localhost:8000/stats
```

---

## 🔄 학습 사이클 실행

### 1. 신호 수집 대기

TradingView에서 신호가 발생하면 자동으로 서버에 전송됩니다.

### 2. 라벨 생성

신호 발생 후 충분한 시간이 지나면 라벨을 생성합니다:

```bash
curl -X POST http://localhost:8000/labels/generate?limit=100
```

또는 Python으로:
```bash
python -c "from server.labeler import label_recent_signals; from server.db import SessionLocal; db=SessionLocal(); print(f'Labeled {label_recent_signals(db, 30)} signals'); db.close()"
```

### 3. 파라미터 최적화

```bash
# BUY 신호 최적화 (50 trials)
python learner/tune.py BUY 50

# 결과: presets/preset_B_candidate.json 생성
```

### 4. Ablation 분석

```bash
python learner/ablation.py

# 결과: docs/ablation_report.md 생성
```

### 5. 대시보드에서 A/B 비교

1. http://localhost:8501 접속
2. "A/B 비교" 탭 선택
3. Current vs Candidate 성능 비교
4. 성능이 우수하면 "승격" 버튼 클릭

### 6. 새 프리셋 적용

1. 대시보드 "프리셋 관리" 탭
2. Candidate 선택
3. Pine Script 코드 복사
4. TradingView 지표에 붙여넣기

---

## 🐛 문제 해결

### ImportError: No module named 'xxx'

```bash
pip install -r requirements.txt
```

### Database locked

SQLite 파일이 잠긴 경우:
```bash
rm vmsi_sdm.db
python -c "from server.db import init_db; init_db()"
```

### Port already in use

다른 포트로 실행:
```bash
# 서버
uvicorn server.app:app --port 8001

# 대시보드
streamlit run dashboard/app.py --server.port 8502
```

### TradingView 신호가 안 들어와요

1. 서버가 외부에서 접근 가능한지 확인
2. ngrok 등으로 로컬 서버 노출:
   ```bash
   ngrok http 8000
   ```
3. TradingView Alert Webhook URL을 ngrok URL로 변경

---

## 📚 더 알아보기

- **상세 문서**: `docs/README.md`
- **시스템 설계**: `docs/DESIGN.md`
- **API 명세**: `docs/API.md`

---

## 🎉 완료!

이제 VMSI-SDM 자가학습형 트레이딩 시스템이 실행 중입니다!

TradingView 차트를 열고 신호를 기다리세요. 🚀

