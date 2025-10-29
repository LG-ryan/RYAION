# 📊 VMSI-SDM Analyst Report System

## 🎯 개요

**증권사 애널리스트 리포트 스타일**의 신호 분석 시스템입니다. 
단순히 "BUY 신호 발생"이 아니라, **왜 그 신호가 나왔는지**, **리스크는 무엇인지**, **어떻게 대응해야 하는지**를 전문적으로 분석합니다.

---

## 🚀 주요 기능

### 1️⃣ **신호 발생 조건 상세 분석**

```
✅ 트렌드 스코어 강함 (>= 60)
✅ RSI 강세권 (62.5 > 60)
✅ 거래량 증가 (1.8x > 1.5x)
✅ EMA 정배열 (차이: +2.35%)
✅ 신뢰 가능한 신호 (68% >= 60%)

→ 종합 평가 점수: 8.2 / 10.0
```

**5가지 핵심 조건**을 체크하고, 각 조건의 달성 여부와 점수를 제공합니다.

---

### 2️⃣ **리스크 평가**

```
⚠️ 중간 거래량 변동성: 거래량이 평균의 1.8배로 증가했습니다. 주의가 필요합니다.
✅ 안정적 가격 변동: VCP 비율 0.42%로 변동성이 낮습니다.
✅ 신고가 근처: 52주 신고가 대비 3.2% 하락으로 상승 추세 지속 가능성 높습니다.
✅ 적정 RSI: RSI 62.5로 적정 수준입니다.

→ 리스크 수준: 🟡 보통 (Moderate)
```

**4가지 리스크 요인**을 평가하고, 종합 리스크 수준을 제공합니다.

---

### 3️⃣ **SL/TP 자동 계산**

```
| 항목                   | 가격        | 비고                 |
|------------------------|-------------|----------------------|
| 진입가 (Entry)         | $5,821.50   | 신호 발생 시점 가격  |
| 손절가 (Stop Loss)     | $5,530.43   | 진입가 대비 -5.00%   |
| 목표가 (Take Profit)   | $6,403.65   | 진입가 대비 +10.00%  |
| 손익비 (R:R Ratio)     | 1:2.00      | 위험 대비 보상 비율  |
```

진입/손절/익절 가격을 명확히 제시합니다.

---

### 4️⃣ **시나리오 분석**

```
🟢 Bull Case (확률: 75%)
트렌드 스코어가 유지되거나 강화되는 경우, 목표가까지 무난히 상승...

🟡 Base Case (확률: 62%)
현재 신호 조건이 그대로 유지되는 경우, 목표가 도달 후 일부 차익 실현...

🔴 Bear Case (확률: 15%)
거시 경제 악재나 갑작스런 악재로 인해 추세가 반전되는 경우...
```

**3가지 시나리오**를 제시하여 투자자가 상황별 대응 방안을 준비할 수 있도록 합니다.

---

### 5️⃣ **실행 계획 (Action Plan)**

```
1. 진입 시점
   - 현재가 ($5,821.50) 부근에서 분할 매수 권고
   - 1차: 50% 진입
   - 2차: RSI 소폭 하락 시 50% 추가 (평단가 낮추기)

2. 손절 조건 (다음 중 하나 충족 시 즉시 청산)
   - 가격이 $5,530.43 이하로 하락
   - EMA 역배열 전환 (EMA1 < EMA2)
   - RSI가 40 이하로 하락

3. 익절 전략
   - 1차 익절: 목표가 $6,403.65 도달 시 50% 청산
   - 2차 익절: 추세 유지 시 trailing stop으로 추가 수익 추구
   - 최종 청산: SELL 신호 발생 시 전량 매도

4. 포지션 사이징
   - 리스크 수준 보통을 고려하여
   - 추천 포지션 크기: 5-10% (총 자산 대비)
```

**구체적인 진입/청산/관리 전략**을 단계별로 제시합니다.

---

## 📖 리포트 구조

### **Full Report Template**

```markdown
# 🟢 SPX 매수 신호 분석 리포트

**VMSI-SDM Research | 기술적 분석 리포트**

---

## 📋 Executive Summary (요약)
- 심볼, 신호 타입, 타임프레임
- 신호 강도, 리스크 수준
- 추천 등급 (⭐⭐⭐ Strong Buy / ⭐⭐ Buy / ⭐ Hold)

---

## 💡 Investment Thesis (투자 논리)
- 왜 이 신호가 발생했나?
- 충족된 조건 5가지
- 종합 평가 점수

---

## 📊 Technical Analysis (기술적 분석)
- 가격 정보 (진입/손절/익절)
- 주요 지표 현황 (Trend Score, Prob, RSI, Vol Mult)

---

## ⚠️ Risk Assessment (리스크 평가)
- 종합 리스크 수준
- 리스크 요인 4가지 (변동성, VCP, ATH 거리, RSI)

---

## 🎯 Scenario Analysis (시나리오 분석)
- Bull Case (강세 시나리오)
- Base Case (기본 시나리오)
- Bear Case (약세 시나리오)

---

## 📈 Action Plan (실행 계획)
- 진입 시점
- 손절 조건
- 익절 전략
- 포지션 사이징

---

## 🎓 Disclaimer (면책조항)
- 투자 권유가 아닌 정보 제공 목적
- 과거 성과는 미래 수익을 보장하지 않음
```

---

## 🎨 사용 방법

### **Step 1: 대시보드 접속**

```bash
http://localhost:8501
```

---

### **Step 2: "신호 모니터링" 탭 선택**

상단 탭에서 **"📊 신호 모니터링"** 클릭

---

### **Step 3: 신호 선택**

```
🔍 신호를 선택하면 상세 애널리스트 리포트를 확인할 수 있습니다

선택박스:
- BUY | SPX (1D) | 2025-10-29 09:30
- BUY | AAPL (1D) | 2025-10-28 16:00
- SELL | TSLA (4H) | 2025-10-27 12:00
...
```

원하는 신호를 선택하면 **즉시 전문 리포트 생성**됩니다.

---

### **Step 4: 리포트 확인**

선택 즉시 화면에 **증권사 스타일 애널리스트 리포트** 표시:

1. 요약 (Executive Summary)
2. 투자 논리 (Investment Thesis)
3. 기술적 분석 (Technical Analysis)
4. 리스크 평가 (Risk Assessment)
5. 시나리오 분석 (Scenario Analysis)
6. 실행 계획 (Action Plan)

---

### **Step 5: 리포트 다운로드 (선택)**

```
📥 리포트 다운로드 (Markdown)
```

버튼 클릭 시 Markdown 파일로 다운로드:
```
signal_report_SPX_BUY_20251029_0930.md
```

---

## 🧠 분석 로직

### **1. 신호 조건 분석 (`analyze_signal_conditions`)**

```python
# BUY 신호 예시
conditions = []

# 1. Trend Score
if trend_score >= 70:
    conditions.append("✅ 트렌드 스코어 매우 강함")
    score = 10
elif trend_score >= 60:
    conditions.append("✅ 트렌드 스코어 강함")
    score = 8
...

# 2. RSI
if rsi > 60:
    conditions.append(f"✅ RSI 강세권 ({rsi:.1f})")
    score = 9
...

# 3-5. Volume, EMA, Probability
...

# 종합 점수 계산
avg_score = sum(scores) / len(scores)

# 강도 평가
if avg_score >= 8:
    strength = "상 (Strong)" 🟢
elif avg_score >= 6:
    strength = "중 (Moderate)" 🟡
else:
    strength = "하 (Weak)" 🔴
```

---

### **2. 리스크 평가 (`assess_risk`)**

```python
risk_factors = []

# 1. 거래량 변동성
if vol_mult > 3.0:
    risk_factors.append("⚠️ 높은 거래량 변동성")
    risk_score = 8
...

# 2. VCP (가격 변동폭)
if vcp_ratio > 0.7:
    risk_factors.append("⚠️ 높은 가격 변동폭")
    risk_score = 8
...

# 3. ATH 거리
if dist_ath > 0.20:
    risk_factors.append("⚠️ 신고가 대비 먼 위치")
    risk_score = 6
...

# 4. RSI 과매수/과매도
if rsi > 75:  # BUY 신호
    risk_factors.append("⚠️ 과매수 경고")
    risk_score = 7
...

# 종합 리스크 평가
avg_risk = sum(risk_scores) / len(risk_scores)

if avg_risk >= 7:
    risk_level = "높음 (High)" 🔴
elif avg_risk >= 5:
    risk_level = "보통 (Moderate)" 🟡
else:
    risk_level = "낮음 (Low)" 🟢
```

---

### **3. SL/TP 계산 (`calculate_sltp`)**

```python
# v3 Clean 형식
entry_price = features.get('price', 0)
sl_price = features.get('sl_price', 0)
tp_price = features.get('tp_price', 0)

# Fallback (v2 형식)
if sl_price == 0:
    sl_price = entry_price * 0.95  # -5%
if tp_price == 0:
    tp_price = entry_price * 1.10  # +10%
```

---

### **4. 시나리오 생성 (`generate_scenarios`)**

```python
# BUY 신호 예시
bull_case = f"""
트렌드 스코어 {trend_score}점이 유지되거나 강화되는 경우,
{symbol}은(는) 목표가(TP)까지 무난히 상승할 것으로 예상됩니다.
목표가 도달 후에도 추세가 유지되면 추가 수익을 노릴 수 있습니다.
"""

base_case = f"""
현재 신호 조건이 그대로 유지되는 경우,
{symbol}은(는) 목표가(TP) +10% 수준까지 상승 후 일부 차익 실현...
"""

bear_case = f"""
거시 경제 악재나 갑작스런 악재로 인해 추세가 반전되는 경우,
{symbol}은(는) 손절가(SL)까지 하락할 수 있습니다.
이 경우 손실을 -5% 수준으로 제한하고 다음 기회를 기다리는 것이 바람직합니다.
"""
```

---

## 💡 활용 팁

### **Tip 1: 리포트 다운로드 후 보관**

```
매 신호마다 리포트를 다운로드하여 보관하면
- 과거 신호 복기 가능
- 나만의 매매 일지 생성
- 개선점 분석
```

---

### **Tip 2: 리스크 수준별 대응**

```
🟢 낮음 (Low):
→ 공격적 포지션 (10-15%)
→ 익절 목표 +15% 이상

🟡 보통 (Moderate):
→ 중립 포지션 (5-10%)
→ 익절 목표 +10%

🔴 높음 (High):
→ 보수적 포지션 (3-5%)
→ 익절 목표 +5-7%
→ 손절 철저 준수
```

---

### **Tip 3: 시나리오별 대응 미리 준비**

```
Bull Case 시:
- 익절 후 포지션 일부 유지
- trailing stop 활용

Base Case 시:
- 목표가 도달 즉시 청산

Bear Case 시:
- 손절가 도달 즉시 청산
- 감정적 판단 금지
```

---

### **Tip 4: 조건 충족 여부 모니터링**

```
리포트의 "조건 충족" 섹션을 보고:

✅ 표시가 많으면 (4-5개):
→ 강한 신호, 신뢰도 높음

⚠️ 표시가 많으면 (2-3개):
→ 보통 신호, 주의 필요

❌ 표시가 있으면:
→ 약한 신호, 재검토 필요
```

---

## 🎯 리포트 품질 평가

### **우수한 리포트 예시**

```
신호 강도: 🟢 상 (Strong) - 8.5/10
리스크 수준: 🟢 낮음 (Low) - 3.2/10
추천 등급: ⭐⭐⭐ Strong Buy

조건 충족:
✅ 트렌드 스코어 매우 강함
✅ RSI 강세권
✅ 거래량 폭증
✅ EMA 강한 정배열
✅ 고확률 신호

→ 이런 신호는 적극 진입 권고!
```

---

### **보통 리포트 예시**

```
신호 강도: 🟡 중 (Moderate) - 6.2/10
리스크 수준: 🟡 보통 (Moderate) - 5.5/10
추천 등급: ⭐⭐ Buy

조건 충족:
✅ 트렌드 스코어 보통
⚠️ RSI 중립
✅ 거래량 증가
✅ EMA 정배열
⚠️ 보통 신호

→ 신중한 진입, 포지션 축소
```

---

### **약한 리포트 예시**

```
신호 강도: 🔴 하 (Weak) - 4.5/10
리스크 수준: 🔴 높음 (High) - 7.8/10
추천 등급: ⭐ Hold

조건 충족:
⚠️ 트렌드 스코어 보통
❌ RSI 약세권
⚠️ 거래량 부족
❌ EMA 역배열
❌ 낮은 신뢰도

→ 진입 보류, 다음 기회 대기
```

---

## 🔄 업데이트 계획

### **v3.1 (계획 중)**

- [ ] AI 기반 뉴스 분석 추가
- [ ] 감성 분석 (Sentiment Analysis)
- [ ] 섹터/업종 비교 분석
- [ ] 과거 유사 패턴 찾기

### **v3.2 (계획 중)**

- [ ] PDF 리포트 생성
- [ ] 이메일 자동 발송
- [ ] 모바일 푸시 알림
- [ ] 슬랙/디스코드 연동

---

## 📚 참고 자료

- `dashboard/signal_analyst.py`: 리포트 생성 로직
- `dashboard/app.py`: 대시보드 UI
- `02_V3_CLEAN_GUIDE.md`: v3 Clean 가이드
- `01_HOW_TO_BACKTEST.md`: 백테스트 가이드

---

## 🎊 결론

**VMSI-SDM Analyst Report System**은 단순한 신호 목록이 아닌, 
**전문 애널리스트 수준의 상세 분석**을 제공합니다.

```
Before:
"BUY 신호 발생" ← 이게 끝

After:
- 왜 발생했는지 (5가지 조건 분석)
- 리스크는 무엇인지 (4가지 요인 평가)
- 어떻게 대응할지 (실행 계획 제시)
- 상황별 시나리오 (Bull/Base/Bear)

→ 완전히 다른 수준의 의사결정 지원!
```

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**버전**: v3.0

🎯 **이제 대시보드에서 신호를 클릭하고 전문 리포트를 확인하세요!** 📊

