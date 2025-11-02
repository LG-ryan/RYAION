# Cursor Instruction — SDM v2 Pine Deliverables (Spec-Driven, No Hand-Coding)
> **역할:** Cursor가 본 문서를 근거로 트레이딩뷰용 **Indicator/Strategy** Pine 스크립트 2종을 생성한다. 우리는 코딩하지 않고 **명세와 품질 기준**만 제시한다.

---

## 0) 목표
- TradingView에 **즉시 붙여넣기 가능한** Pine v5+(v6 호환 지향) 코드 2종 산출
  - **Indicator:** 실시간 신호 감지 · 시각화 · `alert()` Webhook 전송
  - **Strategy:** 동일 로직 기반 백테스트 · SL/TP · 리버스 · 성능 KPI 표시
- 실시간 운영(**웹훅/알림**)과 오프라인 검증(**백테스트/튜닝**) **완전 분리**

---

## 1) 산출물(파일 경로 고정)
1. `pine/indicator_sdm_v2.pine`
2. `pine/strategy_sdm_v2.pine`

> 모든 파일의 헤더에는 버전, 날짜, 설명, 저작권 주석 포함.

---

## 2) 공통 설계 원칙
- **코어 신호 로직 공유:** EMA/RSI/ATR 조합 → 신호 함수는 공통화
- **역할 분리:** Indicator=센서(알림/시각화), Strategy=엔진(포지션/검증)
- **가독성 높은 구조:** 섹션 헤더(Inputs/Core/Signals/Hysteresis/Alert/Plot/BT)
- **안정성:** 초기바/NaN 처리, `max_lines_count`/`max_labels_count` 합리 설정, 불필요 루프 금지
- **일관 네이밍:** `sdm_*` 접두어 권장(예: `sdm_is_buy()`)
- **리페인트 방지 옵션:** 봉마감 기준 운용 선택(Confirm on Close)

---

## 3) 공통 입력(기본값)
- **Trend:** EMA Fast=20, EMA Slow=50
- **Momentum:** RSI Length=14, RSI Buy≥55, RSI Sell≤45
- **Volatility:** ATR Length=14
- **Hysteresis/Cooldown:** Cooldown bars=3, Confirm on close=true
- **표시(Display):** (Indicator만) Show Ribbon=true, Show Labels=true
- **확장 여지:** HTF 컨텍스트(주봉 지지/저항), 프리셋 주입(JSON 문자열)

---

## 4) 신호 정의(공통 알고리즘)
- **추세:** `trendUp = EMA(fast) > EMA(slow)`, `trendDown = EMA(fast) < EMA(slow)`
- **모멘텀:** `RSI >= rsiBuy`(롱 성향), `RSI <= rsiSell`(숏 성향)
- **진입 휴리스틱(기본):**
  - **BuyCond:** `trendUp && RSI>=rsiBuy && close>EMA(fast)`
  - **SellCond:** `trendDown && RSI<=rsiSell && close<EMA(fast)`
- **히스테리시스/쿨다운:** 마지막 시그널 바로부터 `cooldownBars` 미경과 시 신규 신호 금지
- **액션 문자열 표준:** `"BUY" | "SELL" | "HOLD_UP" | "HOLD_DOWN" | "HOLD_FLAT"`

---

## 5) Indicator 요구사항 (실시간 운용/웹훅)
### 5.1 기능
- 차트 오버레이: EMA Fast/Slow 라인, 추세 리본 배경, 신호 라벨
- **Alert 전송:** `alert()`로 JSON 1줄 출력
  - `confirmOnClose=true`면 **봉 마감 시점**에만 알림
  - `cooldownBars` 준수(연속 노이즈 억제)
  - BUY/SELL/관망(HOLD_UP/DOWN/FLAT) 전부 알림 가능(봇 운영 고려)

### 5.2 Alert JSON 스키마(엄격 준수)
```json
{
  "ts_unix": 1730123456,
  "symbol": "BINANCE:BTCUSDT",
  "timeframe": "15",
  "action": "BUY",
  "price": 69123.45,
  "ema_fast": 69001.12,
  "ema_slow": 68444.78,
  "rsi": 58.2,
  "atr": 312.7,
  "bar_state": "close",
  "cooldown_bars": 3,
  "version": "sdm_v2_indicator",
  "meta": {
    "trend": "up",
    "reason": ["trend_up","rsi>=buy","close>ema_fast"]
  }
}
```
- **필수 키:** `ts_unix`, `symbol`, `timeframe`, `action`, `price`, `ema_fast`, `ema_slow`, `rsi`, `atr`, `bar_state`, `version`
- **action 값:** `"BUY"|"SELL"|"HOLD_UP"|"HOLD_DOWN"|"HOLD_FLAT"`
- 문자열은 소문자 스네이크케이스 키, 숫자는 소수 허용

### 5.3 Alert 설정 가이드(코드에 주석으로 안내문 포함)
- TradingView Alerts → **“Any alert() function call”**
- Webhook URL: `{SERVER_BASE_URL}/alert`
- 필요 시 보안 필드: 메시지에 `signature`(HMAC 등) 필드 옵션 제공

### 5.4 표시 옵션
- 리본: trendUp=teal, trendDown=orange(높은 투명도)
- 라벨: BUY/SELL 신호바 상·하단 표시 on/off
- 지표명: `"SDM v2 — Indicator (EMA/RSI/ATR + Hysteresis/Cooldown)"`

### 5.5 안정성/엣지 처리
- `barstate.isconfirmed` 분기 운용(Confirm on Close)
- 초기 바, 저유동성/갭 바, NaN 안전 처리
- 과다 알림 방지(쿨다운, 조건 중복 방지)

---

## 6) Strategy 요구사항 (백테스트/튜닝 데이터)
### 6.1 기능
- Indicator와 동일 신호 로직으로 **포지션** 생성/청산
- **SL/TP 파라미터화:**
  - `SL = ATR(atrLen) * k` (k는 입력값)
  - `TP = RR * SL` (RR은 입력값)
- **포지션 규칙:**
  - BUY → **롱 진입**, SELL → **숏 진입**
  - 반대 신호 시 **리버스 옵션**(기본 on)
  - 동시 보유 금지(롱/숏 중 1회선)
- **거래 비용:** 수수료(기본 0.05%), 슬리피지(1틱) 입력
- **리스크 모델:** 고정 수량 or 고정 달러(입력)

### 6.2 KPI(차트 요약 표시)
- 총 수익률, 승률, Profit Factor, MDD, 평균 R, 평균 보유기간
- 전략명: `"SDM v2 — Strategy (BT: EMA/RSI/ATR, ATR-SL, RR-TP)"`

### 6.3 데이터 수집(튜너 참고, Pine 한계 고려)
- `strategy.closedtrades.*` 합산하여 **프리셋 후보**(rsiBuy/rsiSell/atrK/RR 조합) 성능을 화면 요약(Table/Label)
- Pine 내 **네트워크/파일 출력 금지**(TV 제약). 화면 표시만.

### 6.4 안정성/엣지
- Strategy에서는 `alert()` 사용 지양(혼란 방지)
- 과적합 억제: 기본 파라미터 보수적 설정

---

## 7) 파라미터 권장 기본값
- **Indicator:**
  - EMA(20/50), RSI(14; Buy≥55, Sell≤45), ATR(14)
  - Cooldown=3, ConfirmOnClose=true, ShowRibbon/Labels=true
- **Strategy:**
  - ATR k(SL)=1.5, RR=2.0
  - Commission=0.05%, Slippage=1 tick
  - Reverse on signal change=true

---

## 8) 프리셋 주입 규칙(옵션)
- Indicator에 `"Preset JSON"`(문자열) 입력 필드 제공
  - 존재 시 해당 JSON의 키로 파라미터 오버라이드(형식 오류는 무시)
  - 예) `{"ema_fast":18,"ema_slow":55,"rsi_buy":57,"rsi_sell":43,"atr_len":12,"cooldown":4}`
- 오버라이드 우선순위: **프리셋 > 사용자 입력 > 기본값**

---

## 9) 통합 가이드(Alerts → 서버 → 튜너 → 프리셋)
1) TradingView Alerts: **“Any alert() function call”**  
2) Webhook: `POST {SERVER_BASE_URL}/alert`  
3) 서버: Alert JSON 파싱/저장 → 튜너(`python -m learner.tune`) 실행  
4) 대시보드: Preset_B 후보 확인 → 적합 시 Indicator에 프리셋 주입  
5) 반복: 지표/전략 & 프리셋 동시 고도화 사이클

---

## 10) 품질 기준(수용 테스트 체크리스트)
- [ ] 두 파일이 TV Pine Editor에서 **에러 없이 컴파일/실행**
- [ ] Indicator 알림 JSON이 **스키마 준수**(필수키/타입/1줄 출력)
- [ ] `confirmOnClose=true` 시 봉 마감에만 알림
- [ ] `cooldownBars` 동작으로 연속 알림 억제
- [ ] Strategy에서 SL/TP 정상, 반대 신호 시 리버스 옵션 정상
- [ ] KPI가 차트에서 가독성 있게 표시
- [ ] 섹션 헤더/주석/함수 분리/리소스 효율 준수
- [ ] v5 기본, v6 호환(가능 시) 지향

---

## 11) 비목표(이번 스코프 제외)
- 거래소 주문/체결 API 연동
- Pine 외부 네트워크/파일 I/O
- 복잡 MTF 로직(옵션 훅만 유지)
- 내장 ML(튜너는 백엔드 책임)

---

## 12) 개발 순서(커서 수행 지시)
1. `pine/indicator_sdm_v2.pine` 생성  
   - 입력 → 코어계산 → 신호 → 히스테리시스/쿨다운 → Alert(JSON) → 표시
   - Alert JSON은 본 문서 스키마와 **필드명/타입**을 엄격 준수
2. `pine/strategy_sdm_v2.pine` 생성  
   - 동일 신호 로직 → 포지션/SL/TP/리버스/비용/리스크 → KPI 표시
3. 컴파일/실행 검증  
   - 예제 심볼: `BINANCE:BTCUSDT`, `SPY` / 타임프레임: 1m~1D
   - 경계 조건: 초기바/갭/저유동성/쿨다운
4. 코드 품질 정리  
   - 주석/섹션 헤더/함수화/일관 네이밍(`sdm_*`) 적용

---

## 13) 완료 보고(코드 내 주석으로 남김)
- 파일 헤더: 버전/날짜/설명/저작권
- Indicator: Alert JSON **샘플 1~2개**(주석)
- Strategy: KPI 지표 설명(주석)
- **수용 테스트 8개 항목** 통과 결과 체크(주석)
