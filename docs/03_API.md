# VMSI-SDM API 명세서

## 📡 Webhook Server API

Base URL: `http://localhost:8000`

---

## Endpoints

### 1. Health Check

**GET** `/`

서버 상태 확인

**Response**:
```json
{
  "status": "running",
  "service": "VMSI-SDM Webhook Server",
  "version": "2.0.0",
  "timestamp": "2025-10-29T02:00:00.000Z"
}
```

---

### 2. TradingView Alert 수신

**POST** `/alert`

TradingView에서 전송된 신호를 수신하여 DB에 저장

**Request Body**:
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

**Response**:
```json
{
  "status": "success",
  "signal_id": 42,
  "message": "Signal BUY received for AAPL",
  "received_at": "2025-10-29T02:00:00.000Z"
}
```

**Status Codes**:
- `200 OK`: 신호 수신 성공
- `422 Unprocessable Entity`: 유효하지 않은 데이터
- `500 Internal Server Error`: 서버 오류

---

### 3. 신호 목록 조회

**GET** `/signals`

저장된 신호 목록 조회

**Query Parameters**:
- `limit` (int, optional): 조회할 최대 개수 (기본: 100)
- `signal_type` (str, optional): 신호 타입 필터 (BUY, SELL, WATCH_UP, WATCH_DOWN)
- `symbol` (str, optional): 심볼 필터

**Example**:
```
GET /signals?limit=10&signal_type=BUY&symbol=AAPL
```

**Response**:
```json
[
  {
    "id": 42,
    "ts": "1698624000000",
    "symbol": "AAPL",
    "tf": "1D",
    "signal": "BUY",
    "features": {...},
    "params": {...},
    "created_at": "2025-10-29T02:00:00.000Z"
  },
  ...
]
```

---

### 4. 특정 신호의 라벨 조회

**GET** `/signals/{signal_id}/labels`

특정 신호에 대한 라벨(미래 수익률) 조회

**Path Parameters**:
- `signal_id` (int): 신호 ID

**Example**:
```
GET /signals/42/labels
```

**Response**:
```json
[
  {
    "signal_id": 42,
    "fwd_n": 3,
    "fwd_ret": 0.015,
    "broke_high": false,
    "broke_low": false
  },
  {
    "signal_id": 42,
    "fwd_n": 5,
    "fwd_ret": 0.032,
    "broke_high": true,
    "broke_low": false
  },
  {
    "signal_id": 42,
    "fwd_n": 10,
    "fwd_ret": 0.048,
    "broke_high": true,
    "broke_low": false
  },
  {
    "signal_id": 42,
    "fwd_n": 20,
    "fwd_ret": 0.062,
    "broke_high": true,
    "broke_low": false
  }
]
```

**Status Codes**:
- `200 OK`: 라벨 조회 성공
- `404 Not Found`: 라벨이 없음

---

### 5. 라벨 생성 트리거

**POST** `/labels/generate`

라벨이 없는 신호들에 대해 라벨 생성

**Query Parameters**:
- `limit` (int, optional): 한 번에 처리할 최대 개수 (기본: 100)

**Example**:
```
POST /labels/generate?limit=50
```

**Response**:
```json
{
  "status": "success",
  "labeled_count": 42,
  "message": "Labeled 42 signals"
}
```

---

### 6. 실험 결과 조회

**GET** `/experiments`

Optuna 실험 결과 조회

**Query Parameters**:
- `limit` (int, optional): 조회할 최대 개수 (기본: 20)

**Example**:
```
GET /experiments?limit=10
```

**Response**:
```json
[
  {
    "id": 1,
    "run_id": "run_20251029_020000",
    "params": {
      "rsi_buy_th": 58,
      "vol_mult_buy": 1.8,
      "alpha": 0.85,
      ...
    },
    "metrics": {
      "pf": 1.62,
      "mdd": 0.12,
      "win_rate": 0.66,
      "psu_10": 0.71
    },
    "created_at": "2025-10-29T02:00:00.000Z"
  },
  ...
]
```

---

### 7. 전체 통계 조회

**GET** `/stats`

시스템 전체 통계

**Response**:
```json
{
  "total_signals": 1234,
  "total_labels": 4936,
  "total_experiments": 15,
  "buy_signals": 567,
  "sell_signals": 423,
  "watch_signals": 244
}
```

---

## 🔐 보안

### Webhook Secret (선택사항)

환경변수 `WEBHOOK_SECRET` 설정 시, 다음 헤더 필요:

```
X-Webhook-Secret: your_secret_key
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your_secret_key" \
  -d @alert.json
```

---

## 📝 TradingView Alert 설정

### Alert Message Format

TradingView Alert에서 다음 JSON을 Message로 사용:

```json
{
  "symbol":"{{ticker}}",
  "tf":"{{interval}}",
  "t":"{{time}}",
  "signal":"BUY",
  "features":{
    "trendScore":78.5,
    "prob":0.68,
    "ema20_above_50":true,
    "rsi":58.2,
    "vol_mult":1.7,
    "vcp_ratio":0.54,
    "dist_ath":0.06,
    "macro":{"vix":18.4,"dxy_trend":"down","us10y_trend":"flat","hyg_ief":"bull"}
  },
  "params":{
    "ema1":20,"ema2":50,"rsi":14,"vcp":20,
    "alpha":0.8,"beta":0.35,"gamma":0.7,"delta":0.6,"epsilon":0.8
  }
}
```

**Note**: Pine Script에서 `alert()` 함수로 자동 생성됨

### Webhook URL 설정

TradingView Alert 생성 시:
1. **Condition**: VMSI-SDM v2 지표 선택
2. **Webhook URL**: `http://your-server-ip:8000/alert`
3. **Message**: (Pine Script에서 자동 생성)

---

## 🧪 테스트 예시

### curl로 테스트

```bash
# 1. Health check
curl http://localhost:8000/

# 2. 가짜 신호 전송
curl -X POST http://localhost:8000/alert \
  -H "Content-Type: application/json" \
  -d '{
    "symbol":"AAPL",
    "tf":"1D",
    "t":"1698624000000",
    "signal":"BUY",
    "features":{
      "trendScore":78.5,
      "prob":0.68,
      "ema20_above_50":true,
      "rsi":58.2,
      "vol_mult":1.7,
      "vcp_ratio":0.54,
      "dist_ath":0.06,
      "macro":{"vix":18.4,"dxy_trend":"down","us10y_trend":"flat","hyg_ief":"bull"}
    },
    "params":{
      "ema1":20,"ema2":50,"rsi":14,"vcp":20,
      "alpha":0.8,"beta":0.35,"gamma":0.7,"delta":0.6,"epsilon":0.8
    }
  }'

# 3. 신호 조회
curl http://localhost:8000/signals?limit=5

# 4. 라벨 생성
curl -X POST http://localhost:8000/labels/generate?limit=10

# 5. 통계 조회
curl http://localhost:8000/stats
```

### Python으로 테스트

```python
import requests

# 신호 전송
alert_data = {
    "symbol": "AAPL",
    "tf": "1D",
    "t": "1698624000000",
    "signal": "BUY",
    "features": {...},
    "params": {...}
}

response = requests.post(
    "http://localhost:8000/alert",
    json=alert_data
)

print(response.json())
# {'status': 'success', 'signal_id': 42, ...}
```

---

## 📊 OpenAPI Docs

FastAPI는 자동으로 OpenAPI 문서를 생성합니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔄 Rate Limiting (미래 확장)

현재는 Rate Limiting 없음. 프로덕션 배포 시:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/alert")
@limiter.limit("100/hour")
async def receive_alert(...):
    ...
```

---

**API 문서는 지속적으로 업데이트됩니다. 최신 버전은 `/docs` 엔드포인트를 참조하세요.**

