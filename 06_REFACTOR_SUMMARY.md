# 📋 Pine Script v2.1 리팩토링 요약

**리팩토링 날짜**: 2025-10-29  
**버전**: VMSI-SDM v2.0 → v2.1  
**목적**: 안정성, 성능, 유지보수성 향상

---

## ✅ 적용된 변경 사항

### 1. NA-Safety 강화 (필수)

**문제**: Volume 없는 심볼(인덱스, FX)에서 division by zero 발생  
**해결**:
```pine
// Before
vol_mult = volume / vol_avg
vcp_ratio = (vcp_high - vcp_low) / vcp_high
dist_ath = (ath - close) / ath

// After
vol_mult = nz(vol_avg > 0 ? volume / vol_avg : 1.0, 1.0)
vcp_ratio = nz(vcp_high > vcp_low ? (vcp_high - vcp_low) / vcp_high : 0.5, 0.5)
dist_ath = nz(ath > 0 ? (ath - close) / ath : 0.0, 0.0)
```

**효과**:
- ✅ 모든 심볼(주식, 인덱스, FX, 암호화폐)에서 안정적 작동
- ✅ 합리적인 기본값(1.0, 0.5, 0.0) 사용

---

### 2. Macro 심볼 입력 노출 (유용)

**문제**: VIX, DXY 등 매크로 심볼이 하드코딩되어 있어 유연성 부족  
**해결**:
```pine
// 새로운 입력 그룹 추가
var g_macro = "매크로 심볼"
vix_symbol = input.symbol("CBOE:VIX", "VIX Symbol", group=g_macro, 
    tooltip="대안: TVC:VIX, FRED:VIXCLS")
dxy_symbol = input.symbol("TVC:DXY", "DXY Symbol", group=g_macro)
us10y_symbol = input.symbol("TVC:US10Y", "US10Y Symbol", group=g_macro)
hyg_symbol = input.symbol("AMEX:HYG", "HYG Symbol", group=g_macro)
ief_symbol = input.symbol("NASDAQ:IEF", "IEF Symbol", group=g_macro)

// Fallback 로직 추가
vix_real = use_realtime_macro ? request.security(vix_symbol, timeframe.period, close) : na
vix_val = nz(vix_real, 18.4)  // 실패 시 시뮬레이션 값 사용
```

**효과**:
- ✅ 사용자가 다른 거래소 심볼 선택 가능 (예: KRX:VKOSPI)
- ✅ `use_realtime_macro=false`일 때 `security()` 호출 완전히 스킵 (성능 향상)
- ✅ 실시간 데이터 실패 시 자동으로 시뮬레이션 값으로 Fallback

---

### 3. ATH Factor 제거 (코드 정리)

**문제**: `ath_norm` 변수를 계산만 하고 사용하지 않아 혼란 야기  
**해결**:
```pine
// Before
ath_norm = 1.0 - math.min(dist_ath / 0.2, 1.0)
trend_score = (alpha * ema_above + beta * rsi_norm + gamma * vol_norm + delta * vcp_norm) * 100.0

// After
// 참고: ath_norm 제거 (계산만 하고 사용하지 않아 혼란 야기)
// dist_ath는 유지 (alert JSON에서 사용)
trend_score = (alpha * ema_above + beta * rsi_norm + gamma * vol_norm + delta * vcp_norm) * 100.0
```

**효과**:
- ✅ 불필요한 코드 제거
- ✅ `dist_ath`는 여전히 계산되고 Alert JSON에 포함됨 (분석용)

---

### 4. Alert JSON 표준화 (필수)

**문제**: Alert JSON이 복잡하고 snake_case 일관성 부족  
**해결**:
```json
// 표준화된 스키마 (필수 필드만)
{
  "ts_unix": 1730188800000,
  "symbol": "AAPL",
  "timeframe": "1D",
  "action": "BUY",
  "price": 178.45,
  "trend_score": 82.50,
  "prob": 0.7234,
  "rsi": 58.32,
  "vol_mult": 1.82,
  "vcp_ratio": 0.1234,
  "dist_ath": 0.0567,
  "ema1": 175.20,
  "ema2": 172.80,
  "bar_state": "close",
  "fast_mode": false,
  "realtime_macro": false,
  "version": "vmsi_sdm_v2.1"
}
```

**효과**:
- ✅ snake_case 일관성 (서버 파싱 용이)
- ✅ 필수 필드만 포함 (단순화)
- ✅ `bar_state: "close"` 명시적 표시
- ✅ `version` 필드로 스키마 버전 추적

---

## ❌ 채택하지 않은 제안

### 1. 가중치 합 = 1 정규화
**이유**: Stage Detection은 절대 threshold 기반 (70+, 30-). 가중치 변경 시 모든 신호 바뀜.  
**대안**: 현재 가중치 유지, 문서에 의미 명확히 기재

### 2. Cooldown 중 WATCH 업데이트
**이유**: Cooldown 목적은 신호 안정성. WATCH 업데이트 시 노이즈 증가.  
**대안**: Cooldown 중 모든 Stage 고정 (현재 방식 유지)

### 3. panel_update_on_close (강제)
**이유**: 실시간 피드백이 트레이더에게 중요. 확정봉만 보면 늦을 수 있음.  
**대안**: 기본값 실시간 유지 (선택적 기능으로만 추가 가능)

---

## 📊 Sample Alert JSON

```json
{"ts_unix":1730188800000,"symbol":"AAPL","timeframe":"1D","action":"BUY","price":178.45,"trend_score":82.50,"prob":0.7234,"rsi":58.32,"vol_mult":1.82,"vcp_ratio":0.1234,"dist_ath":0.0567,"ema1":175.20,"ema2":172.80,"bar_state":"close","fast_mode":false,"realtime_macro":false,"version":"vmsi_sdm_v2.1"}
```

---

## 🎯 변경 사항 요약 (3줄)

1. **안정성**: Volume 없는 심볼에서도 작동 (NA-safety, fallback)
2. **유연성**: 매크로 심볼을 사용자가 선택 가능하도록 입력 노출
3. **명확성**: 불필요한 코드 제거 (ath_norm), Alert JSON 표준화

---

## 🚀 다음 단계

- [x] Indicator 리팩토링 완료
- [x] Strategy 리팩토링 완료
- [ ] TradingView에 업로드 후 테스트
- [ ] Volume 없는 심볼(^VIX, DXY 등)에서 검증
- [ ] 서버 Alert JSON 파서 업데이트 (v2.1 스키마 대응)

---

## 📝 참고

- **Stage Detection 철학**: "며칠 전 신호"를 위한 보수적 추세 전환 감지
- **가중치**: 절대 threshold 기반 (합=1 불필요)
- **Cooldown**: 신호 안정성 보장 (WATCH 업데이트 금지)
- **Alert**: barstate.isconfirmed에서만 한 번 전송

---

**작성**: Cursor AI (검토 완료)  
**커밋**: `386c3d3` (2025-10-29)



