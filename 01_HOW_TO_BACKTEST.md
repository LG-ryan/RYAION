# 📈 VMSI-SDM Strategy 백테스트 가이드

## 🎯 목적

**신호의 실제 성능을 확인하고, 매매 파라미터를 조정하는 방법**

---

## 🚀 Step 1: Strategy 추가

### 1. TradingView 차트 열기
```
1. TradingView.com 접속
2. 차트 열기 (예: SPX, AAPL 등)
3. 타임프레임 선택 (예: 1D - 일봉)
```

### 2. Strategy 파일 복사
```
파일: C:\Users\ryanj\RYAION\vmsi-sdm\pine\strategy_sdm_v2.pine
```

### 3. Pine Editor 열기
```
1. 차트 하단 "Pine Editor" 탭 클릭
2. "Open" 클릭 → "New blank indicator"
3. 전체 코드 삭제
4. strategy_sdm_v2.pine 내용 복사 & 붙여넣기
5. "Save" 클릭 → 이름: "VMSI-SDM Strategy v2.1"
6. "Add to Chart" 클릭
```

---

## 📊 Step 2: 백테스트 결과 확인

### 1. Strategy Tester 열기
```
차트 하단 "Strategy Tester" 탭 클릭
```

### 2. 주요 지표 확인

#### **Performance Summary (성과 요약)**
```
Net Profit:           +$15,234  ← 총 수익 (높을수록 좋음)
Net Profit %:         +15.23%   ← 수익률
Total Closed Trades:  48        ← 전체 매매 횟수
Percent Profitable:   65.31%    ← 승률 (60% 이상이면 우수)
Profit Factor:        1.85      ← 손익비 (1.5 이상이면 좋음)
Max Drawdown:         -8.2%     ← 최대 손실 (낮을수록 좋음)
Avg Trade:            +$317.38  ← 평균 수익
```

#### **Risk Metrics (리스크 지표)**
```
Sharpe Ratio:         1.92      ← 위험 대비 수익 (1.5 이상 우수)
Sortino Ratio:        2.45      ← 하방 위험 대비 수익
Calmar Ratio:         1.85      ← MDD 대비 수익
```

#### **Trade Analysis (매매 분석)**
```
Avg Winning Trade:    +$650     ← 평균 수익 매매
Avg Losing Trade:     -$380     ← 평균 손실 매매
Largest Win:          +$2,150   ← 최대 수익
Largest Loss:         -$890     ← 최대 손실
```

---

## 🎯 Step 3: 성능 기준 (좋은 Strategy 판별)

### ✅ **우수한 Strategy**
```
승률 (Win Rate):       > 60%
손익비 (Profit Factor): > 1.5
Sharpe Ratio:          > 1.5
Max Drawdown:          < 15%
총 매매 횟수:           > 30 (통계적 신뢰성)
```

### ⚠️ **개선 필요**
```
승률 (Win Rate):       < 50%
손익비 (Profit Factor): < 1.2
Sharpe Ratio:          < 1.0
Max Drawdown:          > 25%
```

---

## 🔧 Step 4: 파라미터 조정

### 1. 리스크 관리 조정

#### **보수적 (안정성 중시)**
```
Strategy 설정 → 리스크 관리:
- Stop Loss %:     3.0  (더 빨리 손절)
- Take Profit %:   6.0  (더 빨리 익절)

결과:
- 승률 증가 (작은 손실 빠르게 커팅)
- 총 수익 감소 (큰 수익 놓침)
- Max Drawdown 감소
```

#### **공격적 (수익 중시)**
```
Strategy 설정 → 리스크 관리:
- Stop Loss %:     7.0  (손실 여유 더 줌)
- Take Profit %:   15.0 (큰 수익 노림)

결과:
- 승률 감소 (손절 늦어짐)
- 총 수익 증가 (큰 수익 잡음)
- Max Drawdown 증가
```

#### **ATR 기반 (추천 - 변동성 고려)**
```
Strategy 설정 → 리스크 관리:
- Use ATR-based SL/TP: ON
- ATR Length:          14
- ATR SL Multiplier:   2.0 (변동성의 2배로 손절)
- ATR TP Multiplier:   3.0 (변동성의 3배로 익절)

장점:
- 변동성 높을 때 → SL/TP 자동 확대
- 변동성 낮을 때 → SL/TP 자동 축소
- 자산별 특성 반영
```

---

### 2. 신호 필터링 조정

#### **신호 많이 (빈번한 매매)**
```
Strategy 설정 → 파라미터 설정:
- RSI Buy Threshold:   50  (낮춤)
- Volume Mult Buy:     1.2 (낮춤)

결과:
- 매매 횟수 증가
- 승률 감소 (노이즈 많음)
```

#### **신호 적게 (보수적 매매)**
```
Strategy 설정 → 파라미터 설정:
- RSI Buy Threshold:   65  (높임)
- Volume Mult Buy:     2.0 (높임)

결과:
- 매매 횟수 감소
- 승률 증가 (확실한 신호만)
```

---

### 3. Fast Mode (단기 매매용)

```
Strategy 설정 → 모드 설정:
- Fast Mode: ON

효과:
- Hysteresis (신호 유지) 비활성화
- Cooldown (대기 시간) 비활성화
- 신호 즉각 반응

사용 시기:
✅ 단기 매매 (Scalping, Day Trading)
❌ 장기 매매 (Swing, Position) - 오히려 노이즈
```

---

## 📊 Step 5: List of Trades (매매 내역 확인)

### 1. 개별 매매 확인
```
Strategy Tester → "List of Trades" 탭

표시 내용:
- Entry Date:   2025-10-15 09:30  ← 진입 시간
- Exit Date:    2025-10-18 15:00  ← 청산 시간
- Entry Price:  5,821.50          ← 진입 가격
- Exit Price:   6,403.65          ← 청산 가격
- Profit:       +$582.15 (+10%)   ← 수익
- Duration:     3 days 5h 30m     ← 보유 기간
- Exit Reason:  Limit (TP)        ← 청산 이유
```

### 2. 패턴 분석
```
질문:
- 손실 매매의 공통점은? (RSI 낮았나? Vol 적었나?)
- 수익 매매의 공통점은? (특정 시간대? 특정 조건?)
- 최대 손실 발생 시기는? (특정 이벤트? 변동성 급등?)

→ 이 정보를 Optuna 학습에 활용!
```

---

## 🎯 Step 6: 프리셋 테스트

### 1. 자산별 프리셋 비교

```
Strategy 설정 → 프리셋:
- Preset Type: "Equity Swing"    (주식 스윙)
```

**백테스트 실행 → 결과 기록**

```
Strategy 설정 → 프리셋:
- Preset Type: "Index Position"  (지수 포지션)
```

**백테스트 실행 → 결과 비교**

```
비교 예시:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Preset           Net Profit   Win Rate   Sharpe
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Equity Swing     +18.5%       68%        2.1
Index Position   +12.3%       62%        1.8
Custom           +15.2%       65%        1.9
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

결론: Equity Swing이 SPX에 가장 적합!
```

---

## 🚀 Step 7: 실전 적용

### 1. 최적 설정 확정
```
백테스트 결과가 가장 좋았던 설정:
- Preset Type: Equity Swing
- Stop Loss %: 4.0
- Take Profit %: 12.0
- RSI Buy Threshold: 60
- Volume Mult Buy: 1.8
```

### 2. Indicator에도 동일 설정 적용
```
Indicator "VMSI-SDM v2" 설정:
- Strategy와 동일한 파라미터 입력
- Alert 생성 (Webhook)
```

### 3. 실시간 모니터링
```
1. TradingView에서 신호 발생
2. Webhook → FastAPI → SQLite 저장
3. Streamlit 대시보드에서 확인
4. 수동 매매 또는 Strategy 결과 참고
```

---

## 📈 Step 8: 성능 개선 루프

```
Week 1: 초기 백테스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Strategy 추가
- 기본 설정으로 백테스트
- 승률: 52%, Profit Factor: 1.3
```

```
Week 2: 신호 수집 (10개 이상)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- TradingView Alert 활성화
- 실제 신호 수집
- 데이터베이스에 저장
```

```
Week 3: 첫 학습 (run_learning.bat)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Optuna 실행
- preset_B_candidate.json 생성
- Strategy/Indicator 설정 업데이트
```

```
Week 4: 개선 확인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 새 설정으로 백테스트
- 승률: 68%, Profit Factor: 1.85
- 15% 승률 향상! ✅
```

```
Month 2~3: 지속적 개선
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 신호 50개 → 재학습
- 신호 100개 → 재학습
- 승률: 75%, Profit Factor: 2.1
```

---

## 🎓 백테스트 해석 가이드

### **예시 1: 좋은 Strategy**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategy: VMSI-SDM v2 (SPX, 1D)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Net Profit:         +24.5% (vs Buy-Hold: +18.2%)
Win Rate:           68.5%
Profit Factor:      2.15
Max Drawdown:       -6.8%
Sharpe Ratio:       2.34
Total Trades:       52
Avg Hold Time:      4.5 days

평가: ⭐⭐⭐⭐⭐ 우수!
- 시장 대비 초과 수익 (+6.3%)
- 높은 승률 (68.5%)
- 낮은 Drawdown (-6.8%)
→ 실전 적용 가능!
```

### **예시 2: 개선 필요한 Strategy**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategy: VMSI-SDM v2 (AAPL, 15min)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Net Profit:         +3.2% (vs Buy-Hold: +15.8%)
Win Rate:           48.2%
Profit Factor:      1.05
Max Drawdown:       -18.5%
Sharpe Ratio:       0.67
Total Trades:       156
Avg Hold Time:      2.3 hours

평가: ⭐⭐ 불량
- 시장 대비 하락 (-12.6%)
- 낮은 승률 (48.2%)
- 높은 Drawdown (-18.5%)
→ 파라미터 대폭 조정 필요!
```

---

## 💡 Pro Tips

### 1. 심볼별 백테스트
```
각 심볼마다 최적 파라미터가 다릅니다:
- SPX (지수): Equity Swing 또는 Index Position
- AAPL (개별주): Equity Swing
- BTC (암호화폐): Crypto Intraday
- EUR/USD (외환): Forex Scalping

→ 심볼별로 백테스트 후 프리셋 선택!
```

### 2. 타임프레임별 백테스트
```
1D (일봉):   → Position/Swing Trading (TP: 10~20%)
4H (4시간):  → Swing Trading (TP: 5~10%)
1H (1시간):  → Day Trading (TP: 2~5%)
15min:       → Scalping (TP: 0.5~2%)

→ 타임프레임에 맞게 SL/TP 조정!
```

### 3. 기간별 백테스트
```
Full History:    전체 성능 (신뢰도 높음)
Last 3 Months:   최근 시장 적응도
Bear Market:     하락장 성능
Bull Market:     상승장 성능

→ 다양한 시장 환경에서 테스트!
```

---

## 🎯 다음 단계

### **지금 바로:**
1. TradingView 차트 열기
2. strategy_sdm_v2.pine 복사
3. Strategy Tester에서 백테스트 실행
4. 승률, Profit Factor 확인

### **백테스트 결과가 좋으면:**
1. Indicator 설정 동일하게 적용
2. Alert 생성 (Webhook)
3. 신호 수집 시작

### **백테스트 결과가 나쁘면:**
1. 파라미터 조정 (SL/TP, Threshold)
2. 프리셋 변경
3. 재백테스트
4. 개선될 때까지 반복

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**대상**: 백테스트 초보자용

🎯 **이제 Strategy의 실제 성능을 확인하세요!** 📈


