# 🔄 Stage Detection 원래 설계로 복구

## 🚨 문제 상황

### 발견된 문제
```
차트: SPX 주간봉 (2022-2025, 3년)
신호 발생: 수십 개 (거의 매주)
평가: 데이트레이딩 수준으로 변질됨
```

### 사용자 니즈 vs 현재 구현
```
원하는 것: "며칠 전에 신호를 인식해서 사거나 팔거나"
         = Swing Trading (며칠~몇 주 보유)
         = 큰 추세 전환 미리 포착

현재 구현: 매주마다 신호 발생
         = Day Trading 수준
         = Stage Detection의 본질 상실
```

---

## 📖 원래 설계 (VMSI-SDM_FULL_INIT.md)

### 시스템 이름의 의미
```
VMSI-SDM = Volde Momentum Stage Indicator - Stage Detection Model
            ^^^^^^                         ^^^^^
            추세                           단계 감지

핵심 콘셉트: "Stage Detection"
→ 시장의 단계(Stage) 변화를 감지하는 지표
```

### Stage 종류
```
BUY        : 강력한 상승 추세 진입 (매수!)
WATCH_UP   : 상승 관찰 중 (아직 매수 아님, 준비 단계)
WATCH_DOWN : 하락 관찰 중 (아직 매도 아님, 주의 단계)
SELL       : 강력한 하락 추세 진입 (매도!)
```

### 설계 원칙
```
1. 히스테리시스(3봉 평균) → 노이즈 필터링
2. 쿨다운(3봉) → 신호 잦은 변경 방지
3. 리페인트 방지 → 확정봉 기준
4. 중장기 추세 전환 포착 → 몇 주/몇 달에 한 번
```

---

## ❌ 잘못된 방향으로 개발된 이유

### 변경 히스토리
```
1단계: 초기 설정
  - TrendScore >= 70, Prob >= 0.6  (보수적)
  - 히스테리시스 3봉, 쿨다운 3봉
  - 결과: 68회 / 154년

2단계: "신호가 너무 적다"는 피드백
  - TrendScore >= 60, Prob >= 0.55 (완화)
  - vol_mult 조건 제거
  - Fast Mode 추가
  - 결과: 신호 폭증 (데이트레이딩 수준)

문제: Stage Detection의 본질을 잃어버림!
```

---

## ✅ 복구 방안

### Phase 1: 파라미터 복구 (완료)

#### Indicator & Strategy 모두 적용
```pine
// 히스테리시스 & 쿨다운 강화
hysteresis_len = 5  (이전 3 → 5)
cooldown_bars = 10  (이전 3 → 10)

// Stage 조건 강화
BUY: 
  - TrendScore >= 75 (60 → 75)
  - Prob >= 0.65 (0.55 → 0.65)
  - RSI > 55
  - vol_mult > 1.5 (다시 추가)

SELL:
  - TrendScore <= 25 (40 → 25)
  - Prob <= 0.35 (0.45 → 0.35)
  - RSI < 45
  - vol_mult > 1.3 (다시 추가)

WATCH_UP:
  - TrendScore > 55
  - Prob > 0.55

WATCH_DOWN:
  - TrendScore < 45
  - Prob < 0.45
```

---

## 📊 예상 효과

### Before (잘못된 방향)
```
주간봉 기준:
  BUY 신호: 수십 개 / 3년
  신호 빈도: 거의 매주
  Stage: 대부분 BUY 또는 WATCH_UP
  실용성: ❌ 너무 잦은 매매
```

### After (원래 설계)
```
주간봉 기준:
  BUY 신호: 5-10개 / 3년 (예상)
  신호 빈도: 몇 달에 1-2번
  Stage: BUY ↔ WATCH_UP ↔ WATCH_DOWN ↔ SELL 명확히 구분
  실용성: ✅ 중장기 추세 전환 포착
```

---

## 🎯 올바른 사용법

### 1. Fast Mode 끄기!
```
Settings → 모드 설정:
  fast_mode: □ 체크 해제  ← 중요!
```

**Fast Mode는 테스트용입니다!** 실전에서는 끄세요.

### 2. 타임프레임 선택
```
권장 타임프레임:
  - 일봉(Daily): 몇 주에 1-2번 신호
  - 주봉(Weekly): 몇 달에 1-2번 신호
  - 월봉(Monthly): 1-2년에 1-2번 신호

Swing Trading:
  → 일봉 또는 주봉 사용 권장
```

### 3. Stage 해석
```
BUY 신호:
  → 강력한 상승 추세 시작
  → 매수 진입
  → 포지션 유지

WATCH_UP:
  → 상승 관찰 중
  → 아직 매수 아님
  → BUY 신호 대기

WATCH_DOWN:
  → 하락 관찰 중
  → 경계 단계
  → SELL 신호 주의

SELL 신호:
  → 강력한 하락 추세 시작
  → 매도 또는 숏 진입
```

---

## 🔍 Stage Detection의 철학

### 왜 "Stage"인가?

```
시장은 연속적으로 변하지만,
큰 흐름은 "단계(Stage)"로 구분할 수 있습니다.

Stage 1: 바닥권 횡보 (WATCH_DOWN)
Stage 2: 상승 추세 (BUY → WATCH_UP)
Stage 3: 고점권 횡보 (WATCH_UP)
Stage 4: 하락 추세 (SELL → WATCH_DOWN)

VMSI-SDM은 이 Stage 전환을 감지합니다!
```

### 왜 신호가 적어야 하나?

```
많은 신호 = 노이즈
적은 신호 = 중요한 전환점만

목표:
  "진짜 중요한 순간"만 알려주기
  "며칠 전에 미리 알려주기"
  
→ Stage 전환은 자주 일어나지 않습니다!
```

---

## ⚠️ 주의사항

### Fast Mode 사용 금지 (실전)
```
Fast Mode는:
  ✅ 테스트용 (빠른 피드백)
  ✅ 데이터 수집용
  ❌ 실전 트레이딩용

실전에서는:
  → Fast Mode OFF
  → 히스테리시스 & 쿨다운 활성화
```

### 백테스트 결과 해석
```
거래 횟수가 적은 것 = 정상!
  68회 / 154년 = 0.44회/년
  → 너무 적음 (조건 너무 엄격)
  
목표:
  1-2회/년 (주봉 기준)
  5-10회/년 (일봉 기준)
  
→ 현재 설정 (TrendScore 75, Cooldown 10)이 적절
```

---

## 📋 적용 순서

### Step 1: Indicator 업데이트
```
1. TradingView Pine Editor
2. indicator_sdm_v2.pine 복사
3. 저장 및 Update on Chart
```

### Step 2: Strategy 업데이트
```
1. Pine Editor (새 탭)
2. strategy_sdm_v2.pine 복사
3. 저장 및 Add to Chart
```

### Step 3: 설정 확인
```
Settings → 모드 설정:
  fast_mode: □ 체크 해제  ← 필수!
  use_realtime_macro: □ 체크 해제

Settings → 파라미터 설정:
  hysteresis_len: 5
  cooldown_bars: 10
```

### Step 4: 백테스트 재실행
```
Strategy Tester 확인:
  - Total Trades: 10-30회 / 154년 (예상)
  - 신호 간격: 몇 달에 1번
  - 보유 기간: 길어짐
```

---

## 🎯 기대 효과

### Swing Trading에 최적화
```
✅ 큰 추세 전환만 포착
✅ 며칠~몇 주 전에 미리 알림
✅ 잦은 매매 방지
✅ 장기 보유 전략에 적합
```

### Stage Detection 본질 복구
```
✅ BUY: 진짜 강한 상승만
✅ SELL: 진짜 강한 하락만
✅ WATCH: 관찰 단계 명확히
✅ 신호의 신뢰도 향상
```

---

## 💡 핵심 교훈

### 문제의 근본 원인
```
"신호가 너무 적다" → 조건 완화
→ 신호 폭증
→ 본질 상실

교훈: 신호가 적은 것이 정상!
     Stage Detection은 빈번한 신호를 위한 것이 아님!
```

### 올바른 접근
```
VMSI-SDM = Stage Detection
         = 중장기 추세 전환 감지
         = 몇 주/몇 달에 한 번 신호
         
→ 신호가 적다 = 성공
→ 신호가 많다 = 실패
```

---

## 📖 참고 문서

- **VMSI-SDM_FULL_INIT.md**: 원래 설계 문서
- **00_QUICKSTART.md**: 빠른 시작 가이드
- **01_QUICK_FIX.md**: 이전 잘못된 가이드 (무시)

---

**🎯 이제 진짜 "Stage Detection"이 시작됩니다!**

**며칠 전에 큰 추세 전환을 미리 포착하세요!**


