"""
Signal Analyst Report Generator
증권사 애널리스트 스타일 신호 분석 리포트 생성
"""

from datetime import datetime
from typing import Dict, Any, Tuple


class SignalAnalyst:
    """신호 분석 리포트 생성기"""
    
    @staticmethod
    def analyze_signal_conditions(signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        신호 발생 조건 분석
        
        Returns:
            - conditions_met: 충족된 조건 목록
            - conditions_score: 조건 점수
            - strength: 신호 강도 (상/중/하)
        """
        features = signal_data.get('features_json', {})
        signal_type = signal_data.get('signal', 'BUY')
        
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        rsi = features.get('rsi', 50)
        vol_mult = features.get('vol_mult', 1.0)
        ema1 = features.get('ema1', 0)
        ema2 = features.get('ema2', 0)
        prob = features.get('prob', 0.5)
        vcp_ratio = features.get('vcp_ratio', features.get('vcp', 0.5))
        dist_ath = features.get('dist_ath', 0.0)
        
        conditions_met = []
        scores = []
        
        if signal_type == "BUY":
            # 트렌드 조건
            if trend_score >= 70:
                conditions_met.append("✅ 트렌드 스코어 매우 강함 (>= 70)")
                scores.append(10)
            elif trend_score >= 60:
                conditions_met.append("✅ 트렌드 스코어 강함 (>= 60)")
                scores.append(8)
            elif trend_score >= 55:
                conditions_met.append("⚠️ 트렌드 스코어 보통 (>= 55)")
                scores.append(5)
            else:
                conditions_met.append("❌ 트렌드 스코어 약함 (< 55)")
                scores.append(2)
            
            # RSI 조건
            if rsi > 60:
                conditions_met.append(f"✅ RSI 강세권 ({rsi:.1f} > 60)")
                scores.append(9)
            elif rsi > 50:
                conditions_met.append(f"✅ RSI 중립 상단 ({rsi:.1f} > 50)")
                scores.append(7)
            elif rsi > 45:
                conditions_met.append(f"⚠️ RSI 중립 ({rsi:.1f} > 45)")
                scores.append(5)
            else:
                conditions_met.append(f"❌ RSI 약세권 ({rsi:.1f} <= 45)")
                scores.append(2)
            
            # 거래량 조건
            if vol_mult > 2.0:
                conditions_met.append(f"✅ 거래량 폭증 ({vol_mult:.1f}x > 2.0x)")
                scores.append(10)
            elif vol_mult > 1.5:
                conditions_met.append(f"✅ 거래량 증가 ({vol_mult:.1f}x > 1.5x)")
                scores.append(8)
            elif vol_mult > 1.2:
                conditions_met.append(f"✅ 거래량 정상 ({vol_mult:.1f}x > 1.2x)")
                scores.append(6)
            else:
                conditions_met.append(f"⚠️ 거래량 부족 ({vol_mult:.1f}x < 1.2x)")
                scores.append(3)
            
            # EMA 정렬
            if ema1 > ema2:
                diff_pct = ((ema1 - ema2) / ema2) * 100
                if diff_pct > 2:
                    conditions_met.append(f"✅ EMA 강한 정배열 (차이: +{diff_pct:.2f}%)")
                    scores.append(9)
                else:
                    conditions_met.append(f"✅ EMA 정배열 (차이: +{diff_pct:.2f}%)")
                    scores.append(7)
            else:
                conditions_met.append("❌ EMA 역배열 (상승 추세 아님)")
                scores.append(0)
            
            # 확률
            if prob >= 0.70:
                conditions_met.append(f"✅ 고확률 신호 ({prob:.2%} >= 70%)")
                scores.append(10)
            elif prob >= 0.60:
                conditions_met.append(f"✅ 신뢰 가능한 신호 ({prob:.2%} >= 60%)")
                scores.append(7)
            elif prob >= 0.55:
                conditions_met.append(f"⚠️ 보통 신호 ({prob:.2%} >= 55%)")
                scores.append(5)
            else:
                conditions_met.append(f"❌ 낮은 신뢰도 ({prob:.2%} < 55%)")
                scores.append(2)
        
        else:  # SELL
            # 트렌드 조건 (역)
            if trend_score <= 30:
                conditions_met.append("✅ 트렌드 스코어 매우 약함 (<= 30)")
                scores.append(10)
            elif trend_score <= 40:
                conditions_met.append("✅ 트렌드 스코어 약함 (<= 40)")
                scores.append(8)
            elif trend_score <= 45:
                conditions_met.append("⚠️ 트렌드 스코어 보통 (<= 45)")
                scores.append(5)
            else:
                conditions_met.append("❌ 트렌드 스코어 강함 (> 45)")
                scores.append(2)
            
            # RSI 조건 (역)
            if rsi < 40:
                conditions_met.append(f"✅ RSI 약세권 ({rsi:.1f} < 40)")
                scores.append(9)
            elif rsi < 50:
                conditions_met.append(f"✅ RSI 중립 하단 ({rsi:.1f} < 50)")
                scores.append(7)
            elif rsi < 55:
                conditions_met.append(f"⚠️ RSI 중립 ({rsi:.1f} < 55)")
                scores.append(5)
            else:
                conditions_met.append(f"❌ RSI 강세권 ({rsi:.1f} >= 55)")
                scores.append(2)
            
            # 거래량 조건 (동일)
            if vol_mult > 2.0:
                conditions_met.append(f"✅ 거래량 폭증 ({vol_mult:.1f}x > 2.0x)")
                scores.append(10)
            elif vol_mult > 1.5:
                conditions_met.append(f"✅ 거래량 증가 ({vol_mult:.1f}x > 1.5x)")
                scores.append(8)
            elif vol_mult > 1.2:
                conditions_met.append(f"✅ 거래량 정상 ({vol_mult:.1f}x > 1.2x)")
                scores.append(6)
            else:
                conditions_met.append(f"⚠️ 거래량 부족 ({vol_mult:.1f}x < 1.2x)")
                scores.append(3)
            
            # EMA 정렬 (역)
            if ema1 < ema2:
                diff_pct = ((ema2 - ema1) / ema1) * 100
                if diff_pct > 2:
                    conditions_met.append(f"✅ EMA 강한 역배열 (차이: -{diff_pct:.2f}%)")
                    scores.append(9)
                else:
                    conditions_met.append(f"✅ EMA 역배열 (차이: -{diff_pct:.2f}%)")
                    scores.append(7)
            else:
                conditions_met.append("❌ EMA 정배열 (하락 추세 아님)")
                scores.append(0)
            
            # 확률
            if prob <= 0.30:
                conditions_met.append(f"✅ 고확률 신호 ({prob:.2%} <= 30%)")
                scores.append(10)
            elif prob <= 0.40:
                conditions_met.append(f"✅ 신뢰 가능한 신호 ({prob:.2%} <= 40%)")
                scores.append(7)
            elif prob <= 0.45:
                conditions_met.append(f"⚠️ 보통 신호 ({prob:.2%} <= 45%)")
                scores.append(5)
            else:
                conditions_met.append(f"❌ 낮은 신뢰도 ({prob:.2%} > 45%)")
                scores.append(2)
        
        # 강도 평가
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 8:
            strength = "상 (Strong)"
            strength_emoji = "🟢"
        elif avg_score >= 6:
            strength = "중 (Moderate)"
            strength_emoji = "🟡"
        else:
            strength = "하 (Weak)"
            strength_emoji = "🔴"
        
        return {
            'conditions_met': conditions_met,
            'conditions_score': avg_score,
            'strength': strength,
            'strength_emoji': strength_emoji
        }
    
    @staticmethod
    def assess_risk(signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        리스크 평가
        
        Returns:
            - risk_level: 리스크 수준 (낮음/보통/높음)
            - risk_factors: 리스크 요인 목록
            - risk_score: 리스크 점수 (0-10)
        """
        features = signal_data.get('features_json', {})
        
        vol_mult = features.get('vol_mult', 1.0)
        vcp_ratio = features.get('vcp_ratio', features.get('vcp', 0.5))
        dist_ath = features.get('dist_ath', 0.0)
        rsi = features.get('rsi', 50)
        
        risk_factors = []
        risk_scores = []
        
        # 1. 변동성 리스크
        if vol_mult > 3.0:
            risk_factors.append(f"⚠️ **높은 거래량 변동성**: 거래량이 평균의 {vol_mult:.1f}배로 급증했습니다. 과열 가능성이 있습니다.")
            risk_scores.append(8)
        elif vol_mult > 2.0:
            risk_factors.append(f"⚠️ **중간 거래량 변동성**: 거래량이 평균의 {vol_mult:.1f}배로 증가했습니다. 주의가 필요합니다.")
            risk_scores.append(5)
        else:
            risk_factors.append(f"✅ **안정적 거래량**: 거래량이 평균의 {vol_mult:.1f}배로 안정적입니다.")
            risk_scores.append(2)
        
        # 2. VCP (가격 변동성)
        if vcp_ratio > 0.7:
            risk_factors.append(f"⚠️ **높은 가격 변동폭**: VCP 비율 {vcp_ratio:.2%}로 가격 변동성이 큽니다. 손절 폭을 넓게 설정하세요.")
            risk_scores.append(8)
        elif vcp_ratio > 0.5:
            risk_factors.append(f"⚠️ **중간 가격 변동폭**: VCP 비율 {vcp_ratio:.2%}로 보통 수준입니다.")
            risk_scores.append(5)
        else:
            risk_factors.append(f"✅ **안정적 가격 변동**: VCP 비율 {vcp_ratio:.2%}로 변동성이 낮습니다.")
            risk_scores.append(2)
        
        # 3. ATH 거리 (신고가 대비 리스크)
        if dist_ath > 0.20:
            risk_factors.append(f"⚠️ **신고가 대비 먼 위치**: 52주 신고가 대비 {dist_ath:.1%} 하락한 위치입니다. 반등 여력이 있으나 저항선 많을 수 있습니다.")
            risk_scores.append(6)
        elif dist_ath > 0.10:
            risk_factors.append(f"⚠️ **신고가 대비 약간 먼 위치**: 52주 신고가 대비 {dist_ath:.1%} 하락한 위치입니다.")
            risk_scores.append(4)
        elif dist_ath > 0.05:
            risk_factors.append(f"✅ **신고가 근처**: 52주 신고가 대비 {dist_ath:.1%} 하락으로 상승 추세 지속 가능성 높습니다.")
            risk_scores.append(2)
        else:
            risk_factors.append(f"✅ **신고가 경신 중**: 52주 신고가 대비 {dist_ath:.1%} 하락으로 강한 상승 추세입니다.")
            risk_scores.append(1)
        
        # 4. RSI 과매수/과매도
        signal_type = signal_data.get('signal', 'BUY')
        if signal_type == "BUY":
            if rsi > 75:
                risk_factors.append(f"⚠️ **과매수 경고**: RSI {rsi:.1f}로 과매수권입니다. 단기 조정 가능성이 있습니다.")
                risk_scores.append(7)
            elif rsi > 65:
                risk_factors.append(f"⚠️ **과매수 임박**: RSI {rsi:.1f}로 과매수권 근처입니다.")
                risk_scores.append(5)
            else:
                risk_factors.append(f"✅ **적정 RSI**: RSI {rsi:.1f}로 적정 수준입니다.")
                risk_scores.append(2)
        else:  # SELL
            if rsi < 25:
                risk_factors.append(f"⚠️ **과매도 경고**: RSI {rsi:.1f}로 과매도권입니다. 반등 가능성이 있습니다.")
                risk_scores.append(7)
            elif rsi < 35:
                risk_factors.append(f"⚠️ **과매도 임박**: RSI {rsi:.1f}로 과매도권 근처입니다.")
                risk_scores.append(5)
            else:
                risk_factors.append(f"✅ **적정 RSI**: RSI {rsi:.1f}로 적정 수준입니다.")
                risk_scores.append(2)
        
        # 리스크 수준 평가
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 5
        
        if avg_risk >= 7:
            risk_level = "높음 (High)"
            risk_emoji = "🔴"
            risk_color = "#f85149"
        elif avg_risk >= 5:
            risk_level = "보통 (Moderate)"
            risk_emoji = "🟡"
            risk_color = "#fb8500"
        else:
            risk_level = "낮음 (Low)"
            risk_emoji = "🟢"
            risk_color = "#2ea043"
        
        return {
            'risk_level': risk_level,
            'risk_emoji': risk_emoji,
            'risk_color': risk_color,
            'risk_factors': risk_factors,
            'risk_score': avg_risk
        }
    
    @staticmethod
    def calculate_sltp(signal_data: Dict[str, Any]) -> Tuple[float, float, float]:
        """
        SL/TP 계산
        
        Returns:
            (entry_price, sl_price, tp_price)
        """
        features = signal_data.get('features_json', {})
        signal_type = signal_data.get('signal', 'BUY')
        
        # v3 Clean 형식
        entry_price = features.get('price', 0)
        sl_price = features.get('sl_price', 0)
        tp_price = features.get('tp_price', 0)
        
        # v2 형식 (fallback)
        if entry_price == 0:
            # 가격 정보가 없으면 EMA로 추정
            entry_price = features.get('ema1', 0)
        
        if sl_price == 0 and entry_price > 0:
            # 기본 SL: -5%
            sl_price = entry_price * 0.95 if signal_type == "BUY" else entry_price * 1.05
        
        if tp_price == 0 and entry_price > 0:
            # 기본 TP: +10%
            tp_price = entry_price * 1.10 if signal_type == "BUY" else entry_price * 0.90
        
        return entry_price, sl_price, tp_price
    
    @staticmethod
    def generate_scenarios(signal_data: Dict[str, Any]) -> Dict[str, str]:
        """
        시나리오 분석 생성
        
        Returns:
            - bull_case: 강세 시나리오
            - base_case: 기본 시나리오
            - bear_case: 약세 시나리오
        """
        signal_type = signal_data.get('signal', 'BUY')
        symbol = signal_data.get('symbol', 'SYMBOL')
        features = signal_data.get('features_json', {})
        
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        prob = features.get('prob', 0.5)
        
        if signal_type == "BUY":
            bull_case = f"""
**🟢 Bull Case (확률: {prob*1.2:.0%})**

트렌드 스코어 {trend_score:.0f}점이 유지되거나 강화되는 경우, {symbol}은(는) 목표가(TP)까지 무난히 상승할 것으로 예상됩니다. 
거래량이 지속적으로 증가하고 EMA 정배열이 유지된다면, **추가 상승 여력**이 있습니다. 
목표가 도달 후에도 추세가 유지되면 포지션 일부를 유지하여 **추가 수익**을 노릴 수 있습니다.
"""
            
            base_case = f"""
**🟡 Base Case (확률: {prob:.0%})**

현재 신호 조건이 그대로 유지되는 경우, {symbol}은(는) 목표가(TP) +10% 수준까지 상승 후 일부 차익 실현 물량이 나올 것으로 예상됩니다. 
이 시나리오에서는 **목표가 도달 시 청산**하는 것이 안전합니다. 
변동성이 예상되므로 손절가(SL)를 철저히 준수하시기 바랍니다.
"""
            
            bear_case = f"""
**🔴 Bear Case (확률: {(1-prob)*0.8:.0%})**

거시 경제 악재나 갑작스런 악재로 인해 추세가 반전되는 경우, {symbol}은(는) 손절가(SL)까지 하락할 수 있습니다. 
RSI가 급격히 하락하거나 EMA 역배열로 전환되면 즉시 청산을 권고합니다. 
이 경우 **손실을 -5% 수준으로 제한**하고 다음 기회를 기다리는 것이 바람직합니다.
"""
        else:  # SELL
            bull_case = f"""
**🟢 Bull Case (확률: {(1-prob)*1.2:.0%})**

하락 추세가 강화되는 경우, {symbol}은(는) 목표가(TP)까지 하락할 것으로 예상됩니다. 
거래량이 증가하며 EMA 역배열이 강화된다면, **추가 하락 여력**이 있습니다. 
목표가 도달 후에도 하락 추세가 유지되면 포지션 일부를 유지하여 **추가 수익**을 노릴 수 있습니다.
"""
            
            base_case = f"""
**🟡 Base Case (확률: {1-prob:.0%})**

현재 신호 조건이 그대로 유지되는 경우, {symbol}은(는) 목표가(TP) -10% 수준까지 하락 후 일부 저점 매수 물량이 나올 것으로 예상됩니다. 
이 시나리오에서는 **목표가 도달 시 청산**하는 것이 안전합니다.
"""
            
            bear_case = f"""
**🔴 Bear Case (확률: {prob*0.8:.0%})**

예상과 달리 반등이 나오는 경우, {symbol}은(는) 손절가(SL)까지 상승할 수 있습니다. 
RSI가 급격히 상승하거나 EMA 정배열로 전환되면 즉시 청산을 권고합니다. 
이 경우 **손실을 -5% 수준으로 제한**하고 다음 기회를 기다리는 것이 바람직합니다.
"""
        
        return {
            'bull_case': bull_case.strip(),
            'base_case': base_case.strip(),
            'bear_case': bear_case.strip()
        }
    
    @staticmethod
    def generate_report(signal_data: Dict[str, Any]) -> str:
        """
        증권사 스타일 애널리스트 리포트 생성
        
        Args:
            signal_data: 신호 데이터 (DB Signal 객체를 dict로 변환)
        
        Returns:
            Markdown 형식의 리포트
        """
        # 기본 정보
        symbol = signal_data.get('symbol', 'UNKNOWN')
        signal_type = signal_data.get('signal', 'BUY')
        tf = signal_data.get('tf', '1D')
        created_at = signal_data.get('created_at', datetime.now())
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # 분석 수행
        conditions = SignalAnalyst.analyze_signal_conditions(signal_data)
        risk_assessment = SignalAnalyst.assess_risk(signal_data)
        entry_price, sl_price, tp_price = SignalAnalyst.calculate_sltp(signal_data)
        scenarios = SignalAnalyst.generate_scenarios(signal_data)
        
        # 리포트 생성
        signal_emoji = "🟢" if signal_type == "BUY" else "🔴"
        signal_korean = "매수" if signal_type == "BUY" else "매도"
        
        report = f"""
# {signal_emoji} {symbol} {signal_korean} 신호 분석 리포트

**VMSI-SDM Research | 기술적 분석 리포트**

---

## 📋 Executive Summary (요약)

| 항목 | 내용 |
|------|------|
| **심볼** | `{symbol}` |
| **신호 타입** | **{signal_type}** ({signal_korean}) |
| **타임프레임** | {tf} |
| **신호 발생 시각** | {created_at.strftime('%Y-%m-%d %H:%M:%S')} |
| **신호 강도** | {conditions['strength_emoji']} **{conditions['strength']}** |
| **리스크 수준** | {risk_assessment['risk_emoji']} **{risk_assessment['risk_level']}** |
| **추천 등급** | {'⭐⭐⭐ Strong Buy' if conditions['conditions_score'] >= 8 and signal_type == 'BUY' else ('⭐⭐ Buy' if conditions['conditions_score'] >= 6 and signal_type == 'BUY' else ('⭐⭐⭐ Strong Sell' if conditions['conditions_score'] >= 8 and signal_type == 'SELL' else ('⭐⭐ Sell' if conditions['conditions_score'] >= 6 and signal_type == 'SELL' else '⭐ Hold')))} |

---

## 💡 Investment Thesis (투자 논리)

### Why This Signal? (왜 이 신호가 발생했나?)

본 신호는 VMSI-SDM 시스템의 다중 기술적 지표 분석을 통해 생성되었습니다. 
다음 **{len(conditions['conditions_met'])}가지 조건**이 충족되어 {signal_korean} 신호가 발생하였습니다:

"""
        
        # 조건 목록 추가
        for i, condition in enumerate(conditions['conditions_met'], 1):
            report += f"{i}. {condition}\n"
        
        report += f"""

**종합 평가 점수: {conditions['conditions_score']:.1f} / 10.0**

---

## 📊 Technical Analysis (기술적 분석)

### 가격 정보

| 항목 | 가격 | 비고 |
|------|------|------|
| **진입가 (Entry)** | `${entry_price:,.2f}` | 신호 발생 시점 가격 |
| **손절가 (Stop Loss)** | `${sl_price:,.2f}` | 진입가 대비 {((sl_price / entry_price - 1) * 100):.2f}% |
| **목표가 (Take Profit)** | `${tp_price:,.2f}` | 진입가 대비 {((tp_price / entry_price - 1) * 100):.2f}% |
| **손익비 (R:R Ratio)** | `1:{abs((tp_price - entry_price) / (entry_price - sl_price)):.2f}` | 위험 대비 보상 비율 |

### 주요 지표 현황

"""
        
        features = signal_data.get('features_json', {})
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        prob = features.get('prob', 0.5)
        rsi = features.get('rsi', 50)
        vol_mult = features.get('vol_mult', 1.0)
        
        report += f"""
- **Trend Score**: {trend_score:.1f} / 100
  - 의미: {'강한 상승 추세' if trend_score >= 70 else ('상승 추세' if trend_score >= 60 else ('중립' if trend_score >= 45 else '하락 추세'))}
  
- **Probability**: {prob:.2%}
  - 의미: {'고확률 신호 (매우 신뢰)' if prob >= 0.7 or prob <= 0.3 else ('신뢰 가능한 신호' if prob >= 0.6 or prob <= 0.4 else '보통 신뢰도 신호')}
  
- **RSI(14)**: {rsi:.1f}
  - 의미: {'과매수 경고' if rsi > 70 else ('강세권' if rsi > 60 else ('중립권' if rsi > 40 else '약세권'))}
  
- **Volume Multiplier**: {vol_mult:.2f}x
  - 의미: {'거래량 폭증 (이례적)' if vol_mult > 3 else ('거래량 증가 (관심 증가)' if vol_mult > 2 else ('정상 거래량' if vol_mult > 1.2 else '거래량 부족'))}

---

## ⚠️ Risk Assessment (리스크 평가)

**종합 리스크 수준: {risk_assessment['risk_emoji']} {risk_assessment['risk_level']}**

"""
        
        for i, factor in enumerate(risk_assessment['risk_factors'], 1):
            report += f"{i}. {factor}\n\n"
        
        report += f"""
---

## 🎯 Scenario Analysis (시나리오 분석)

{scenarios['bull_case']}

{scenarios['base_case']}

{scenarios['bear_case']}

---

## 📈 Action Plan (실행 계획)

### 추천 포지션 관리

"""
        
        if signal_type == "BUY":
            report += f"""
1. **진입 시점**
   - 현재가 (`${entry_price:,.2f}`) 부근에서 분할 매수 권고
   - 1차: 50% 진입
   - 2차: RSI 소폭 하락 시 50% 추가 (평단가 낮추기)

2. **손절 조건** (다음 중 하나 충족 시 즉시 청산)
   - 가격이 `${sl_price:,.2f}` 이하로 하락
   - EMA 역배열 전환 (EMA1 < EMA2)
   - RSI가 40 이하로 하락

3. **익절 전략**
   - 1차 익절: 목표가 `${tp_price:,.2f}` 도달 시 50% 청산
   - 2차 익절: 추세 유지 시 trailing stop으로 추가 수익 추구
   - 최종 청산: SELL 신호 발생 시 전량 매도

4. **포지션 사이징**
   - 리스크 수준 {risk_assessment['risk_level']}를 고려하여
   - 추천 포지션 크기: {'10-15%' if risk_assessment['risk_score'] < 5 else ('5-10%' if risk_assessment['risk_score'] < 7 else '3-5%')} (총 자산 대비)
"""
        else:  # SELL
            report += f"""
1. **진입 시점**
   - 현재가 (`${entry_price:,.2f}`) 부근에서 매도 포지션 진입 권고
   - 또는 인버스/숏 ETF 매수

2. **손절 조건** (다음 중 하나 충족 시 즉시 청산)
   - 가격이 `${sl_price:,.2f}` 이상으로 상승
   - EMA 정배열 전환 (EMA1 > EMA2)
   - RSI가 60 이상으로 상승

3. **익절 전략**
   - 1차 익절: 목표가 `${tp_price:,.2f}` 도달 시 50% 청산
   - 2차 익절: 하락 추세 유지 시 trailing stop으로 추가 수익 추구
   - 최종 청산: BUY 신호 발생 시 전량 청산

4. **포지션 사이징**
   - 리스크 수준 {risk_assessment['risk_level']}를 고려하여
   - 추천 포지션 크기: {'10-15%' if risk_assessment['risk_score'] < 5 else ('5-10%' if risk_assessment['risk_score'] < 7 else '3-5%')} (총 자산 대비)
"""
        
        report += f"""
---

## 🎓 Disclaimer (면책조항)

본 리포트는 VMSI-SDM 시스템의 기술적 분석 결과를 바탕으로 자동 생성된 참고 자료입니다. 
투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 하며, 
본 리포트는 투자 권유가 아닌 정보 제공 목적으로만 제공됩니다.

**과거 성과가 미래 수익을 보장하지 않습니다.**

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Analyst**: VMSI-SDM Automated System v3.0  
**Classification**: Technical Analysis | For Reference Only

---
"""
        
        return report.strip()

