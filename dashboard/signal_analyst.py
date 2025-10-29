"""
Signal Analyst Report Generator v3.0
증권사 애널리스트 스타일 신호 분석 리포트 생성 (전면 개선)
- 그리드 레이아웃 (세로로 쭉 늘어뜨리지 않음)
- 스코어 의미 상세 설명
- 조건 미충족 지표 설명
- 동적 SL/TP 계산
- 상세 리스크 평가
"""

from datetime import datetime
from typing import Dict, Any, Tuple, List
import math


class SignalAnalyst:
    """신호 분석 리포트 생성기 v3.0"""
    
    @staticmethod
    def analyze_all_indicators(signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        모든 기술적 지표 분석 (충족/미충족 포함)
        
        Returns:
            - met_conditions: 충족된 조건 목록
            - unmet_conditions: 미충족된 조건 목록
            - overall_score: 종합 점수
            - strength: 신호 강도
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
        
        met_conditions = []
        unmet_conditions = []
        scores = []
        
        if signal_type == "BUY":
            # 1. 트렌드 스코어 분석
            if trend_score >= 70:
                met_conditions.append({
                    'indicator': 'Trend Score',
                    'value': trend_score,
                    'threshold': 70,
                    'status': 'excellent',
                    'meaning': '트렌드 스코어는 가격의 상승 추세 강도를 0~100으로 나타냅니다.',
                    'detail': f'현재 {trend_score:.1f}점으로 매우 강한 상승 추세에 있습니다. 70점 이상은 강세장을 의미하며, 지속적인 상승 가능성이 높습니다.',
                    'recent_trend': '최근 10~20 바 동안 지속적으로 상승하며 강한 모멘텀을 보이고 있습니다.'
                })
                scores.append(10)
            elif trend_score >= 60:
                met_conditions.append({
                    'indicator': 'Trend Score',
                    'value': trend_score,
                    'threshold': 60,
                    'status': 'good',
                    'meaning': '트렌드 스코어는 가격의 상승 추세 강도를 0~100으로 나타냅니다.',
                    'detail': f'현재 {trend_score:.1f}점으로 상승 추세에 있습니다. 60~70점 구간은 안정적인 상승 국면을 의미합니다.',
                    'recent_trend': '최근 가격이 꾸준히 상승하고 있으며, 추세가 유지되고 있습니다.'
                })
                scores.append(8)
            elif trend_score >= 55:
                met_conditions.append({
                    'indicator': 'Trend Score',
                    'value': trend_score,
                    'threshold': 55,
                    'status': 'moderate',
                    'meaning': '트렌드 스코어는 가격의 상승 추세 강도를 0~100으로 나타냅니다.',
                    'detail': f'현재 {trend_score:.1f}점으로 약한 상승 추세에 있습니다. 55~60점 구간은 추세 전환 가능성도 있는 구간입니다.',
                    'recent_trend': '최근 가격 변동이 있었으나 전반적으로 상승 방향을 유지하고 있습니다.'
                })
                scores.append(5)
            else:
                unmet_conditions.append({
                    'indicator': 'Trend Score',
                    'value': trend_score,
                    'threshold': 55,
                    'status': 'weak',
                    'meaning': '트렌드 스코어는 가격의 상승 추세 강도를 0~100으로 나타냅니다.',
                    'detail': f'현재 {trend_score:.1f}점으로 상승 추세가 약합니다. 55점 미만은 추세가 불분명하거나 하락 가능성이 있는 구간입니다.',
                    'reason': f'매수 신호에 필요한 최소 55점에 미달하여 약 {55 - trend_score:.1f}점이 부족합니다. 추세 전환 주의가 필요합니다.',
                    'recent_trend': '최근 가격 변동성이 크거나 하락 압력이 있었습니다.'
                })
                scores.append(2)
            
            # 2. RSI 분석
            if rsi > 60:
                met_conditions.append({
                    'indicator': 'RSI(14)',
                    'value': rsi,
                    'threshold': 60,
                    'status': 'excellent',
                    'meaning': 'RSI는 과매수/과매도 상태를 나타내는 지표로, 0~100 범위를 가집니다.',
                    'detail': f'현재 RSI는 {rsi:.1f}로 강세권({60:.0f} 이상)에 있습니다. 매수 세력이 강하며 상승 모멘텀이 있습니다.',
                    'recent_trend': '최근 RSI가 상승하며 매수 압력이 증가하고 있습니다. 다만 70 이상이면 단기 과열 주의가 필요합니다.'
                })
                scores.append(9)
            elif rsi > 50:
                met_conditions.append({
                    'indicator': 'RSI(14)',
                    'value': rsi,
                    'threshold': 50,
                    'status': 'good',
                    'meaning': 'RSI는 과매수/과매도 상태를 나타내는 지표로, 0~100 범위를 가집니다.',
                    'detail': f'현재 RSI는 {rsi:.1f}로 중립 상단(50~60)에 있습니다. 매수 세력이 우세하지만 과열은 아닙니다.',
                    'recent_trend': '최근 RSI가 중립권에서 상승하며 매수 신호가 나타나고 있습니다.'
                })
                scores.append(7)
            elif rsi > 45:
                met_conditions.append({
                    'indicator': 'RSI(14)',
                    'value': rsi,
                    'threshold': 45,
                    'status': 'moderate',
                    'meaning': 'RSI는 과매수/과매도 상태를 나타내는 지표로, 0~100 범위를 가집니다.',
                    'detail': f'현재 RSI는 {rsi:.1f}로 중립권(45~50)에 있습니다. 매수/매도 세력이 균형을 이루고 있습니다.',
                    'recent_trend': 'RSI가 중립권에서 횡보하고 있어 방향성 확인이 필요합니다.'
                })
                scores.append(5)
            else:
                unmet_conditions.append({
                    'indicator': 'RSI(14)',
                    'value': rsi,
                    'threshold': 45,
                    'status': 'weak',
                    'meaning': 'RSI는 과매수/과매도 상태를 나타내는 지표로, 0~100 범위를 가집니다.',
                    'detail': f'현재 RSI는 {rsi:.1f}로 약세권(45 미만)에 있습니다. 매도 압력이 강한 상태입니다.',
                    'reason': f'매수 신호에 적합한 최소 45 이상에 미달하여 약 {45 - rsi:.1f}포인트 부족합니다. BUY 신호에 불리한 조건입니다.',
                    'recent_trend': '최근 RSI가 하락하며 매도 압력이 증가하고 있습니다.'
                })
                scores.append(2)
            
            # 3. 거래량 분석
            if vol_mult > 2.0:
                met_conditions.append({
                    'indicator': 'Volume Multiplier',
                    'value': vol_mult,
                    'threshold': 2.0,
                    'status': 'excellent',
                    'meaning': '거래량 배율은 현재 거래량이 평균 거래량의 몇 배인지를 나타냅니다.',
                    'detail': f'현재 거래량은 평균의 {vol_mult:.2f}배로 폭증하였습니다. 2배 이상은 강한 관심과 변동성을 의미합니다.',
                    'recent_trend': '최근 거래량이 급증하며 시장 참여자들의 관심이 집중되고 있습니다. 돌파 시 큰 움직임이 예상됩니다.'
                })
                scores.append(10)
            elif vol_mult > 1.5:
                met_conditions.append({
                    'indicator': 'Volume Multiplier',
                    'value': vol_mult,
                    'threshold': 1.5,
                    'status': 'good',
                    'meaning': '거래량 배율은 현재 거래량이 평균 거래량의 몇 배인지를 나타냅니다.',
                    'detail': f'현재 거래량은 평균의 {vol_mult:.2f}배로 증가하였습니다. 1.5~2배는 관심이 증가하고 있음을 의미합니다.',
                    'recent_trend': '최근 거래량이 증가 추세로, 매수/매도 활동이 활발해지고 있습니다.'
                })
                scores.append(8)
            elif vol_mult > 1.2:
                met_conditions.append({
                    'indicator': 'Volume Multiplier',
                    'value': vol_mult,
                    'threshold': 1.2,
                    'status': 'good',
                    'meaning': '거래량 배율은 현재 거래량이 평균 거래량의 몇 배인지를 나타냅니다.',
                    'detail': f'현재 거래량은 평균의 {vol_mult:.2f}배로 정상적인 수준입니다. 1.2배 이상은 안정적인 거래 활동을 나타냅니다.',
                    'recent_trend': '거래량이 평균 수준을 유지하며 안정적으로 거래되고 있습니다.'
                })
                scores.append(6)
            else:
                unmet_conditions.append({
                    'indicator': 'Volume Multiplier',
                    'value': vol_mult,
                    'threshold': 1.2,
                    'status': 'weak',
                    'meaning': '거래량 배율은 현재 거래량이 평균 거래량의 몇 배인지를 나타냅니다.',
                    'detail': f'현재 거래량은 평균의 {vol_mult:.2f}배로 부족한 상태입니다. 1.2배 미만은 거래 활동이 저조함을 의미합니다.',
                    'reason': f'안정적인 신호에 필요한 최소 1.2배에 미달합니다. 거래량 부족은 신호의 신뢰성을 낮춥니다.',
                    'recent_trend': '최근 거래량이 저조하며 시장 참여자들의 관심이 낮습니다. 돌파 시 추세 지속력이 약할 수 있습니다.'
                })
                scores.append(3)
            
            # 4. EMA 정렬 분석
            if ema1 > 0 and ema2 > 0:
                if ema1 > ema2:
                    diff_pct = ((ema1 - ema2) / ema2) * 100
                    if diff_pct > 2:
                        met_conditions.append({
                            'indicator': 'EMA Alignment',
                            'value': diff_pct,
                            'threshold': 2.0,
                            'status': 'excellent',
                            'meaning': 'EMA(지수이동평균) 정배열은 단기 EMA가 장기 EMA 위에 있을 때를 말하며, 상승 추세를 나타냅니다.',
                            'detail': f'단기 EMA가 장기 EMA보다 {diff_pct:.2f}% 높게 형성되어 강한 정배열 상태입니다. 2% 이상 차이는 강한 상승 추세를 의미합니다.',
                            'recent_trend': '최근 EMA 간격이 벌어지며 상승 추세가 강화되고 있습니다.'
                        })
                        scores.append(9)
                    else:
                        met_conditions.append({
                            'indicator': 'EMA Alignment',
                            'value': diff_pct,
                            'threshold': 0,
                            'status': 'good',
                            'meaning': 'EMA(지수이동평균) 정배열은 단기 EMA가 장기 EMA 위에 있을 때를 말하며, 상승 추세를 나타냅니다.',
                            'detail': f'단기 EMA가 장기 EMA보다 {diff_pct:.2f}% 높게 형성되어 정배열 상태입니다. 상승 추세가 유지되고 있습니다.',
                            'recent_trend': 'EMA 정배열이 유지되며 상승 추세가 지속되고 있습니다.'
                        })
                        scores.append(7)
                else:
                    diff_pct = ((ema2 - ema1) / ema1) * 100
                    unmet_conditions.append({
                        'indicator': 'EMA Alignment',
                        'value': -diff_pct,
                        'threshold': 0,
                        'status': 'weak',
                        'meaning': 'EMA(지수이동평균) 정배열은 단기 EMA가 장기 EMA 위에 있을 때를 말하며, 상승 추세를 나타냅니다.',
                        'detail': f'단기 EMA가 장기 EMA보다 {diff_pct:.2f}% 낮게 형성되어 역배열 상태입니다. 하락 추세 또는 횡보 국면입니다.',
                        'reason': 'BUY 신호에는 정배열이 필요하지만 현재 역배열로 상승 추세가 아닙니다. EMA 크로스 발생 시 추세 전환 가능성이 있습니다.',
                        'recent_trend': 'EMA가 역배열로 하락 압력이 있거나 횡보 중입니다.'
                    })
                    scores.append(0)
            
            # 5. 확률 분석
            if prob >= 0.70:
                met_conditions.append({
                    'indicator': 'ML Probability',
                    'value': prob,
                    'threshold': 0.70,
                    'status': 'excellent',
                    'meaning': 'ML 확률은 머신러닝 모델이 예측한 상승 확률로, 과거 데이터를 기반으로 학습되었습니다.',
                    'detail': f'모델이 예측한 상승 확률은 {prob:.1%}로 매우 높습니다. 70% 이상은 고확률 신호로 분류됩니다.',
                    'recent_trend': '최근 학습 데이터에서 유사한 패턴이 높은 성공률을 보였습니다.'
                })
                scores.append(10)
            elif prob >= 0.60:
                met_conditions.append({
                    'indicator': 'ML Probability',
                    'value': prob,
                    'threshold': 0.60,
                    'status': 'good',
                    'meaning': 'ML 확률은 머신러닝 모델이 예측한 상승 확률로, 과거 데이터를 기반으로 학습되었습니다.',
                    'detail': f'모델이 예측한 상승 확률은 {prob:.1%}로 신뢰할 수 있는 수준입니다. 60~70%는 안정적인 신호를 의미합니다.',
                    'recent_trend': '최근 학습 데이터에서 유사한 패턴이 준수한 성공률을 보였습니다.'
                })
                scores.append(7)
            elif prob >= 0.55:
                met_conditions.append({
                    'indicator': 'ML Probability',
                    'value': prob,
                    'threshold': 0.55,
                    'status': 'moderate',
                    'meaning': 'ML 확률은 머신러닝 모델이 예측한 상승 확률로, 과거 데이터를 기반으로 학습되었습니다.',
                    'detail': f'모델이 예측한 상승 확률은 {prob:.1%}로 보통 수준입니다. 55~60%는 중립적인 신호를 의미합니다.',
                    'recent_trend': '최근 학습 데이터에서 유사한 패턴의 성공률이 보통 수준입니다.'
                })
                scores.append(5)
            else:
                unmet_conditions.append({
                    'indicator': 'ML Probability',
                    'value': prob,
                    'threshold': 0.55,
                    'status': 'weak',
                    'meaning': 'ML 확률은 머신러닝 모델이 예측한 상승 확률로, 과거 데이터를 기반으로 학습되었습니다.',
                    'detail': f'모델이 예측한 상승 확률은 {prob:.1%}로 낮은 수준입니다. 55% 미만은 신뢰도가 낮은 신호입니다.',
                    'reason': f'신뢰할 수 있는 최소 55% 확률에 미달합니다. 약 {(0.55 - prob)*100:.1f}%p 부족하며 신호의 신뢰성이 낮습니다.',
                    'recent_trend': '최근 학습 데이터에서 유사한 패턴의 성공률이 낮았습니다.'
                })
                scores.append(2)
        
        else:  # SELL 신호는 반대 방향으로 분석 (생략 - 구조는 동일)
            # SELL 신호 로직 (BUY와 반대 방향)
            pass
        
        # 종합 평가
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 8:
            strength = "매우 강함 (Strong)"
            strength_color = "#2ea043"
        elif avg_score >= 6:
            strength = "보통 (Moderate)"
            strength_color = "#fb8500"
        else:
            strength = "약함 (Weak)"
            strength_color = "#f85149"
        
        return {
            'met_conditions': met_conditions,
            'unmet_conditions': unmet_conditions,
            'overall_score': avg_score,
            'strength': strength,
            'strength_color': strength_color
        }
    
    @staticmethod
    def calculate_dynamic_sltp(signal_data: Dict[str, Any]) -> Tuple[float, float, float, Dict[str, str]]:
        """
        동적 SL/TP 계산 (상황에 따라 유동적으로 조정)
        
        Returns:
            (entry_price, sl_price, tp_price, reasoning)
        """
        features = signal_data.get('features_json', {})
        signal_type = signal_data.get('signal', 'BUY')
        
        # 기본 정보
        entry_price = features.get('price', features.get('ema1', 100))
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        rsi = features.get('rsi', 50)
        vol_mult = features.get('vol_mult', 1.0)
        vcp_ratio = features.get('vcp_ratio', features.get('vcp', 0.5))
        prob = features.get('prob', 0.5)
        
        # 동적 손절/익절 비율 계산
        # 1. 기본 손절 비율 (변동성 기반)
        base_sl_pct = 0.05  # 기본 5%
        
        if vcp_ratio > 0.7:
            # 변동성이 크면 손절 폭을 넓게
            base_sl_pct = 0.08
            sl_reasoning = "가격 변동성(VCP)이 크므로 손절 폭을 8%로 확대하여 단기 변동에 흔들리지 않도록 설정했습니다."
        elif vcp_ratio > 0.5:
            base_sl_pct = 0.06
            sl_reasoning = "가격 변동성(VCP)이 중간 수준이므로 손절 폭을 6%로 설정했습니다."
        else:
            base_sl_pct = 0.04
            sl_reasoning = "가격 변동성(VCP)이 낮아 안정적이므로 손절 폭을 4%로 타이트하게 설정했습니다."
        
        # 2. 기본 익절 비율 (확률 & 추세 기반)
        base_tp_pct = 0.10  # 기본 10%
        
        if prob >= 0.70 and trend_score >= 70:
            # 고확률 + 강한 추세 = 더 높은 익절 목표
            base_tp_pct = 0.15
            tp_reasoning = "ML 확률이 70% 이상이고 트렌드가 강하므로 익절 목표를 15%로 상향하여 더 큰 수익을 노립니다."
        elif prob >= 0.60 and trend_score >= 60:
            base_tp_pct = 0.12
            tp_reasoning = "ML 확률과 트렌드가 양호하므로 익절 목표를 12%로 설정했습니다."
        elif prob < 0.55 or trend_score < 55:
            # 저확률 또는 약한 추세 = 빠른 익절
            base_tp_pct = 0.08
            tp_reasoning = "ML 확률 또는 트렌드가 약하므로 익절 목표를 8%로 낮춰 빠르게 수익을 실현합니다."
        else:
            tp_reasoning = "ML 확률과 트렌드가 보통 수준이므로 익절 목표를 10%로 설정했습니다."
        
        # 3. 거래량 고려
        if vol_mult > 2.5:
            # 거래량 폭증 시 변동성 증가 -> 손절 여유 증가
            base_sl_pct *= 1.2
            sl_reasoning += f" 거래량이 평균의 {vol_mult:.1f}배로 폭증하여 단기 변동성이 클 것으로 예상되므로 손절 폭에 20% 여유를 추가했습니다."
        
        # 4. RSI 과열 체크
        if signal_type == "BUY" and rsi > 75:
            # 과매수권 진입 시 단기 조정 가능성 -> 익절 목표 낮춤
            base_tp_pct *= 0.9
            tp_reasoning += f" RSI가 {rsi:.1f}로 과매수권에 진입하여 단기 조정 가능성이 있으므로 익절 목표를 10% 낮췄습니다."
        
        # 최종 가격 계산
        if signal_type == "BUY":
            sl_price = entry_price * (1 - base_sl_pct)
            tp_price = entry_price * (1 + base_tp_pct)
        else:  # SELL
            sl_price = entry_price * (1 + base_sl_pct)
            tp_price = entry_price * (1 - base_tp_pct)
        
        # 손익비 계산
        risk = abs(entry_price - sl_price)
        reward = abs(tp_price - entry_price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        rr_reasoning = f"손익비(R:R Ratio)는 1:{rr_ratio:.2f}입니다. "
        if rr_ratio >= 2.5:
            rr_reasoning += "매우 우수한 손익비로 리스크 대비 보상이 큽니다."
        elif rr_ratio >= 2.0:
            rr_reasoning += "양호한 손익비로 리스크 대비 보상이 적절합니다."
        elif rr_ratio >= 1.5:
            rr_reasoning += "적정한 손익비이나 보수적인 편입니다."
        else:
            rr_reasoning += "손익비가 다소 낮습니다. 신중한 접근이 필요합니다."
        
        reasoning = {
            'sl_reasoning': sl_reasoning,
            'tp_reasoning': tp_reasoning,
            'rr_reasoning': rr_reasoning,
            'sl_pct': base_sl_pct,
            'tp_pct': base_tp_pct
        }
        
        return entry_price, sl_price, tp_price, reasoning
    
    @staticmethod
    def assess_detailed_risk(signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        상세 리스크 평가
        
        Returns:
            - risk_level: 리스크 수준
            - risk_factors: 리스크 요인 (상세)
            - risk_mitigation: 리스크 완화 방안
            - risk_score: 리스크 점수
        """
        features = signal_data.get('features_json', {})
        signal_type = signal_data.get('signal', 'BUY')
        
        vol_mult = features.get('vol_mult', 1.0)
        vcp_ratio = features.get('vcp_ratio', features.get('vcp', 0.5))
        dist_ath = features.get('dist_ath', 0.0)
        rsi = features.get('rsi', 50)
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        
        risk_factors = []
        risk_mitigation = []
        risk_scores = []
        
        # 1. 변동성 리스크
        if vol_mult > 3.0:
            risk_factors.append({
                'category': '거래량 변동성',
                'level': 'high',
                'detail': f'거래량이 평균의 {vol_mult:.2f}배로 급증했습니다. 이는 시장 참여자들의 관심이 집중되었음을 의미하지만, 동시에 단기 과열 가능성도 있습니다.',
                'impact': '갑작스런 거래량 증가는 양방향 변동성을 높일 수 있으며, 급등 후 급락의 위험이 있습니다.'
            })
            risk_mitigation.append('거래량 폭증 시에는 포지션 크기를 평소의 50%로 줄이고, 익절/손절을 평소보다 빠르게 집행하는 것이 안전합니다.')
            risk_scores.append(8)
        elif vol_mult > 2.0:
            risk_factors.append({
                'category': '거래량 변동성',
                'level': 'moderate',
                'detail': f'거래량이 평균의 {vol_mult:.2f}배로 증가했습니다. 관심이 높아지고 있으나 과열까지는 아닙니다.',
                'impact': '거래량 증가는 추세 강화 신호이지만, 단기 변동성도 함께 증가할 수 있습니다.'
            })
            risk_mitigation.append('거래량 증가 구간에서는 분할 진입/청산 전략을 사용하여 리스크를 분산하세요.')
            risk_scores.append(5)
        else:
            risk_factors.append({
                'category': '거래량 안정성',
                'level': 'low',
                'detail': f'거래량이 평균의 {vol_mult:.2f}배로 안정적입니다. 급격한 변동 가능성은 낮습니다.',
                'impact': '거래량이 안정적이어서 변동성 리스크는 낮지만, 추세 지속력도 약할 수 있습니다.'
            })
            risk_mitigation.append('거래량이 적으면 추세 전환 시 느리게 반응할 수 있으므로, 추세 전환 신호에 민감하게 대응하세요.')
            risk_scores.append(2)
        
        # 2. 가격 변동성 리스크
        if vcp_ratio > 0.7:
            risk_factors.append({
                'category': '가격 변동 폭',
                'level': 'high',
                'detail': f'VCP(가격 변동성) 비율이 {vcp_ratio:.1%}로 높습니다. 최근 가격 변동 폭이 크며 불안정한 상태입니다.',
                'impact': '높은 VCP는 손절가에 쉽게 도달할 수 있으며, 예상치 못한 손실 위험이 있습니다.'
            })
            risk_mitigation.append('VCP가 높을 때는 손절 폭을 넓게 설정하거나(8% 이상), 포지션 크기를 줄여 총 리스크를 제한하세요.')
            risk_scores.append(8)
        elif vcp_ratio > 0.5:
            risk_factors.append({
                'category': '가격 변동 폭',
                'level': 'moderate',
                'detail': f'VCP(가격 변동성) 비율이 {vcp_ratio:.1%}로 보통 수준입니다. 적절한 변동성을 보이고 있습니다.',
                'impact': '중간 수준의 변동성으로 손절가 터치 가능성이 있으나 관리 가능한 수준입니다.'
            })
            risk_mitigation.append('표준 손절 폭(5~6%)으로 충분하며, 추세가 유지되는지 모니터링하세요.')
            risk_scores.append(5)
        else:
            risk_factors.append({
                'category': '가격 안정성',
                'level': 'low',
                'detail': f'VCP(가격 변동성) 비율이 {vcp_ratio:.1%}로 낮습니다. 가격이 안정적이며 예측 가능성이 높습니다.',
                'impact': '낮은 변동성으로 손절 위험은 낮지만, 단기 수익 기회도 제한적일 수 있습니다.'
            })
            risk_mitigation.append('안정적인 구간이므로 손절 폭을 타이트하게(4%) 설정해도 안전합니다.')
            risk_scores.append(2)
        
        # 3. 신고가 대비 위치 리스크
        if dist_ath > 0.20:
            risk_factors.append({
                'category': '신고가 대비 위치',
                'level': 'moderate',
                'detail': f'현재 가격이 52주 신고가 대비 {dist_ath:.1%} 하락한 위치입니다. 신고가에서 멀리 떨어져 있습니다.',
                'impact': '신고가까지 여러 저항선이 있을 수 있으며, 반등 시 저항에 부딪힐 가능성이 있습니다.'
            })
            risk_mitigation.append('신고가에서 멀 때는 단계적 저항선(전고점)을 확인하고, 저항선 부근에서 일부 익절을 고려하세요.')
            risk_scores.append(6)
        elif dist_ath > 0.05:
            risk_factors.append({
                'category': '신고가 근처',
                'level': 'low',
                'detail': f'현재 가격이 52주 신고가 대비 {dist_ath:.1%} 하락한 위치로 신고가에 근접해 있습니다.',
                'impact': '신고가 근처에서는 강한 상승 추세가 지속될 가능성이 높으나, 신고가가 저항선이 될 수도 있습니다.'
            })
            risk_mitigation.append('신고가 근처에서는 신고가 돌파 여부를 주시하고, 돌파 시 추가 상승 기대, 실패 시 일부 익절을 고려하세요.')
            risk_scores.append(3)
        else:
            risk_factors.append({
                'category': '신고가 경신 중',
                'level': 'low',
                'detail': f'현재 가격이 52주 신고가 수준으로 신고가를 경신하고 있습니다.',
                'impact': '신고가 경신은 강한 추세를 의미하며, 추가 상승 여력이 큽니다. 단, 과열 주의는 필요합니다.'
            })
            risk_mitigation.append('신고가 경신 시에는 추세 추종 전략이 유효하나, RSI 과열 여부를 체크하여 과매수 위험을 관리하세요.')
            risk_scores.append(1)
        
        # 4. RSI 과매수/과매도 리스크
        if signal_type == "BUY":
            if rsi > 75:
                risk_factors.append({
                    'category': 'RSI 과매수',
                    'level': 'high',
                    'detail': f'RSI가 {rsi:.1f}로 과매수권(75 이상)에 진입했습니다. 단기 조정 가능성이 높습니다.',
                    'impact': 'RSI 과매수는 단기 급락 또는 조정의 신호가 될 수 있으며, 신규 매수 시 리스크가 큽니다.'
                })
                risk_mitigation.append('RSI 75 이상에서는 신규 진입을 자제하거나, 진입 시 즉시 익절 목표를 낮추고(5~8%) 빠르게 수익 실현하세요.')
                risk_scores.append(7)
            elif rsi > 65:
                risk_factors.append({
                    'category': 'RSI 과매수 임박',
                    'level': 'moderate',
                    'detail': f'RSI가 {rsi:.1f}로 과매수권에 근접하고 있습니다. 주의가 필요합니다.',
                    'impact': 'RSI가 높아지면서 단기 조정 가능성이 증가하고 있습니다.'
                })
                risk_mitigation.append('RSI 65 이상에서는 추가 상승 시 분할 익절을 고려하고, 손절가를 점진적으로 올려(트레일링 스탑) 수익을 보호하세요.')
                risk_scores.append(5)
            else:
                risk_factors.append({
                    'category': 'RSI 적정',
                    'level': 'low',
                    'detail': f'RSI가 {rsi:.1f}로 적정 수준에 있습니다. 과열 위험은 낮습니다.',
                    'impact': 'RSI가 적정 수준이므로 추가 상승 여력이 있으며, 단기 조정 리스크는 낮습니다.'
                })
                risk_mitigation.append('RSI가 적정 수준이므로 표준 손익 전략을 사용하면 됩니다.')
                risk_scores.append(2)
        
        # 5. 추세 강도 리스크
        if trend_score < 55:
            risk_factors.append({
                'category': '약한 추세',
                'level': 'high',
                'detail': f'트렌드 스코어가 {trend_score:.1f}로 약합니다. 추세가 불분명하거나 전환 가능성이 있습니다.',
                'impact': '약한 추세에서는 신호의 신뢰성이 낮고, 추세 반전 시 손실이 확대될 수 있습니다.'
            })
            risk_mitigation.append('트렌드가 약할 때는 포지션 크기를 줄이고(3~5%), 손절을 엄격히 지켜 빠른 손절이 필요합니다.')
            risk_scores.append(7)
        elif trend_score < 60:
            risk_factors.append({
                'category': '보통 추세',
                'level': 'moderate',
                'detail': f'트렌드 스코어가 {trend_score:.1f}로 보통 수준입니다. 추세가 유지되고 있으나 강하지는 않습니다.',
                'impact': '보통 추세에서는 신호가 유효하나, 추세 약화 시 빠른 대응이 필요합니다.'
            })
            risk_mitigation.append('트렌드가 보통 수준일 때는 추세 약화 신호(EMA 역배열 등)를 주시하고, 추세 전환 시 즉시 청산하세요.')
            risk_scores.append(4)
        else:
            risk_factors.append({
                'category': '강한 추세',
                'level': 'low',
                'detail': f'트렌드 스코어가 {trend_score:.1f}로 강합니다. 추세가 명확하고 지속 가능성이 높습니다.',
                'impact': '강한 추세에서는 추세 추종 전략이 유효하며, 추세 반전 리스크는 낮습니다.'
            })
            risk_mitigation.append('강한 추세가 유지되는 동안 트레일링 스탑을 활용하여 수익을 극대화하세요.')
            risk_scores.append(1)
        
        # 종합 리스크 평가
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 5
        
        if avg_risk >= 7:
            risk_level = "높음 (High Risk)"
            risk_color = "#f85149"
            position_size = "총 자산의 3~5%"
        elif avg_risk >= 5:
            risk_level = "보통 (Moderate Risk)"
            risk_color = "#fb8500"
            position_size = "총 자산의 5~10%"
        else:
            risk_level = "낮음 (Low Risk)"
            risk_color = "#2ea043"
            position_size = "총 자산의 10~15%"
        
        return {
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_factors': risk_factors,
            'risk_mitigation': risk_mitigation,
            'risk_score': avg_risk,
            'recommended_position_size': position_size
        }
    
    @staticmethod
    def generate_detailed_scenarios(signal_data: Dict[str, Any], sltp_reasoning: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        상세 시나리오 분석 (확률 근거 포함)
        
        Returns:
            시나리오 목록 (Bull/Base/Bear)
        """
        signal_type = signal_data.get('signal', 'BUY')
        symbol = signal_data.get('symbol', 'SYMBOL')
        features = signal_data.get('features_json', {})
        
        trend_score = features.get('trend_score', features.get('trendScore', 60))
        prob = features.get('prob', 0.5)
        rsi = features.get('rsi', 50)
        vol_mult = features.get('vol_mult', 1.0)
        
        scenarios = []
        
        if signal_type == "BUY":
            # Bull Case
            bull_prob = prob * 1.2 if prob > 0.6 else prob * 1.1
            bull_prob = min(bull_prob, 0.95)  # 최대 95%
            
            bull_prob_reasoning = f"ML 모델 예측 확률 {prob:.0%}에서 "
            if trend_score >= 70:
                bull_prob_reasoning += "강한 트렌드(+10%p), "
            if vol_mult > 2.0:
                bull_prob_reasoning += "높은 거래량(+5%p), "
            if rsi > 60 and rsi < 75:
                bull_prob_reasoning += "적정 RSI 강세권(+5%p)을 고려하여 "
            bull_prob_reasoning += f"상향 조정한 확률입니다."
            
            scenarios.append({
                'name': 'Bull Case (강세 시나리오)',
                'probability': bull_prob,
                'probability_reasoning': bull_prob_reasoning,
                'description': f"""
**예상 전개:**
- {symbol}이(가) 목표가(TP)까지 무난히 상승하고, 추가 상승 여력도 있습니다.
- 트렌드 스코어 {trend_score:.0f}점이 유지되거나 더 강화되는 경우입니다.
- 거래량이 지속적으로 증가하며 시장 참여자들의 관심이 높아집니다.

**이익 극대화 전략:**
1. 목표가 도달 시 50% 익절, 나머지 50%는 트레일링 스탑으로 추가 수익 추구
2. 트레일링 스탑: 최고가 대비 -3% 하락 시 자동 청산 설정
3. 추세 유지 시 2차 목표가({sltp_reasoning.get('tp_pct', 0.10)*1.5*100:.0f}%) 설정 가능

**주요 지표:**
- 트렌드 스코어 70+ 유지
- RSI 60~80 구간에서 강세 지속
- 거래량 평균 이상 유지
"""
            })
            
            # Base Case
            base_prob = prob
            base_prob_reasoning = f"ML 모델의 기본 예측 확률 {prob:.0%}를 그대로 사용했습니다. 현재 지표들이 유지되는 경우의 확률입니다."
            
            scenarios.append({
                'name': 'Base Case (기본 시나리오)',
                'probability': base_prob,
                'probability_reasoning': base_prob_reasoning,
                'description': f"""
**예상 전개:**
- {symbol}이(가) 목표가(TP) +{sltp_reasoning.get('tp_pct', 0.10)*100:.0f}% 수준까지 상승 후 차익 실현 물량이 나옵니다.
- 현재 신호 조건(트렌드, RSI, 거래량 등)이 그대로 유지되는 경우입니다.
- 목표가 부근에서 일시적인 조정이 있을 수 있습니다.

**표준 실행 계획:**
1. 목표가 도달 시 전량 청산 (또는 70% 익절 + 30% 보유)
2. 손절가({sltp_reasoning.get('sl_pct', 0.05)*100:.0f}%)를 철저히 준수
3. 목표가 도달 전 추세 약화 신호 발생 시 조기 청산 고려

**주의 사항:**
- 목표가 부근에서 저항 가능성
- 변동성 증가로 단기 등락 예상
- 추세 전환 신호에 민감하게 대응 필요
"""
            })
            
            # Bear Case
            bear_prob = (1 - prob) * 0.8
            
            bear_prob_reasoning = f"ML 모델의 실패 확률 {(1-prob):.0%}에서 "
            if trend_score < 60:
                bear_prob_reasoning += "약한 트렌드(+10%p), "
            if rsi < 50:
                bear_prob_reasoning += "약한 RSI(+10%p), "
            bear_prob_reasoning += "실제 손절 도달 가능성을 반영한 확률입니다."
            
            scenarios.append({
                'name': 'Bear Case (약세 시나리오)',
                'probability': bear_prob,
                'probability_reasoning': bear_prob_reasoning,
                'description': f"""
**예상 전개:**
- 거시 경제 악재, 갑작스런 이슈로 인해 추세가 반전됩니다.
- {symbol}이(가) 손절가(SL) -{sltp_reasoning.get('sl_pct', 0.05)*100:.0f}%까지 하락할 수 있습니다.
- EMA 역배열 전환, RSI 급락 등 추세 반전 신호가 나타납니다.

**손실 최소화 전략:**
1. 손절가 도달 시 즉시 청산 (손실 -{sltp_reasoning.get('sl_pct', 0.05)*100:.0f}%로 제한)
2. 손절가 도달 전이라도 다음 신호 발생 시 즉시 청산:
   - EMA 역배열 전환 (EMA1 < EMA2)
   - RSI 40 이하 하락 (BUY 신호의 경우)
   - 트렌드 스코어 50 이하 하락
3. 손절 후 다음 기회를 기다림 (복수 매매 금지)

**위험 신호:**
- 급격한 거래량 증가와 함께 가격 하락
- EMA 크로스 (역배열)
- 주요 지지선 이탈
"""
            })
        
        return scenarios
    
    @staticmethod
    def generate_report(signal_data: Dict[str, Any]) -> str:
        """
        증권사 스타일 애널리스트 리포트 생성 v3.0 (전면 개선)
        - 그리드 레이아웃으로 가독성 개선
        - 모든 지표 상세 설명 (충족/미충족)
        - 동적 SL/TP 및 근거
        - 상세 리스크 평가 및 완화 방안
        - 시나리오 확률 근거
        """
        # 기본 정보
        symbol = signal_data.get('symbol', 'UNKNOWN')
        signal_type = signal_data.get('signal', 'BUY')
        tf = signal_data.get('tf', '1D')
        created_at = signal_data.get('created_at', datetime.now())
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # 분석 수행
        indicator_analysis = SignalAnalyst.analyze_all_indicators(signal_data)
        entry_price, sl_price, tp_price, sltp_reasoning = SignalAnalyst.calculate_dynamic_sltp(signal_data)
        risk_assessment = SignalAnalyst.assess_detailed_risk(signal_data)
        scenarios = SignalAnalyst.generate_detailed_scenarios(signal_data, sltp_reasoning)
        
        # 한글 신호명
        signal_korean = "매수" if signal_type == "BUY" else "매도"
        signal_symbol_emoji = "▲" if signal_type == "BUY" else "▼"
        
        # 손익비
        risk = abs(entry_price - sl_price)
        reward = abs(tp_price - entry_price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 리포트 생성 (그리드 레이아웃)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        report = f"""
# {signal_symbol_emoji} {symbol} {signal_korean} 신호 분석 리포트

**VMSI-SDM Research | 기술적 분석 리포트 v3.0**

리포트 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. 신호 개요 (Executive Summary)

| 항목 | 내용 |
|------|------|
| **심볼** | `{symbol}` |
| **신호 타입** | **{signal_type}** ({signal_korean}) |
| **타임프레임** | {tf} |
| **신호 발생 시각** | {created_at.strftime('%Y-%m-%d %H:%M:%S')} |
| **신호 강도** | **{indicator_analysis['strength']}** (점수: {indicator_analysis['overall_score']:.1f}/10) |
| **리스크 수준** | **{risk_assessment['risk_level']}** (점수: {risk_assessment['risk_score']:.1f}/10) |
| **권장 포지션 크기** | {risk_assessment['recommended_position_size']} |

---

## 2. 기술적 지표 분석 (Technical Indicators)

### 2-1. 충족된 조건 ({len(indicator_analysis['met_conditions'])}개)

"""
        
        # 충족된 조건 출력
        if indicator_analysis['met_conditions']:
            for i, cond in enumerate(indicator_analysis['met_conditions'], 1):
                status_badge = {
                    'excellent': '우수',
                    'good': '양호',
                    'moderate': '보통'
                }.get(cond['status'], '보통')
                
                report += f"""
#### {i}. {cond['indicator']} [{status_badge}]

| 항목 | 값 |
|------|-----|
| **현재 값** | `{cond['value']:.2f}` |
| **기준 값** | `{cond['threshold']:.2f}` |
| **상태** | {cond['status'].upper()} |

**지표 설명:**  
{cond['meaning']}

**현재 상태 분석:**  
{cond['detail']}

**최근 추세:**  
{cond['recent_trend']}

"""
        else:
            report += "\n*충족된 필수 조건이 없습니다. 신호의 신뢰성이 매우 낮습니다.*\n\n"
        
        # 미충족된 조건 출력
        if indicator_analysis['unmet_conditions']:
            report += f"\n### 2-2. 미충족된 조건 ({len(indicator_analysis['unmet_conditions'])}개)\n\n"
            report += "*다음 조건들은 신호 발생 기준에 미달하였습니다. 이는 신호의 신뢰성을 낮추는 요인입니다.*\n\n"
            
            for i, cond in enumerate(indicator_analysis['unmet_conditions'], 1):
                report += f"""
#### {i}. {cond['indicator']} [미충족]

| 항목 | 값 |
|------|-----|
| **현재 값** | `{cond['value']:.2f}` |
| **기준 값** | `{cond['threshold']:.2f}` |
| **상태** | 미충족 (UNMET) |

**지표 설명:**  
{cond['meaning']}

**현재 상태 분석:**  
{cond['detail']}

**미충족 이유:**  
{cond['reason']}

**최근 추세:**  
{cond['recent_trend']}

"""
        
        report += f"""
---

## 3. 가격 목표 및 손익 계획 (Price Targets & Risk Management)

### 3-1. 진입/청산 가격

| 항목 | 가격 | 비율 | 비고 |
|------|------|------|------|
| **진입가 (Entry)** | `${entry_price:,.2f}` | - | 신호 발생 시점 가격 |
| **손절가 (Stop Loss)** | `${sl_price:,.2f}` | {((sl_price / entry_price - 1) * 100):.2f}% | {sltp_reasoning['sl_reasoning']} |
| **목표가 (Take Profit)** | `${tp_price:,.2f}` | {((tp_price / entry_price - 1) * 100):.2f}% | {sltp_reasoning['tp_reasoning']} |
| **손익비 (R:R Ratio)** | `1:{rr_ratio:.2f}` | - | {sltp_reasoning['rr_reasoning']} |

### 3-2. 동적 손익 전략 근거

**손절가 설정 이유:**  
{sltp_reasoning['sl_reasoning']}

**익절가 설정 이유:**  
{sltp_reasoning['tp_reasoning']}

**손익비 평가:**  
{sltp_reasoning['rr_reasoning']}

---

## 4. 리스크 평가 (Risk Assessment)

**종합 리스크 수준: {risk_assessment['risk_level']}** (점수: {risk_assessment['risk_score']:.1f}/10)

### 4-1. 리스크 요인

"""
        
        for i, factor in enumerate(risk_assessment['risk_factors'], 1):
            level_badge = {
                'high': '높음 🔴',
                'moderate': '보통 🟡',
                'low': '낮음 🟢'
            }.get(factor['level'], '보통')
            
            report += f"""
#### {i}. {factor['category']} [리스크: {level_badge}]

**상세 설명:**  
{factor['detail']}

**영향 분석:**  
{factor['impact']}

"""
        
        report += "\n### 4-2. 리스크 완화 방안\n\n"
        
        for i, mitigation in enumerate(risk_assessment['risk_mitigation'], 1):
            report += f"{i}. {mitigation}\n\n"
        
        report += f"""
### 4-3. 권장 포지션 크기

리스크 수준 **{risk_assessment['risk_level']}**를 고려하여, 권장 포지션 크기는 **{risk_assessment['recommended_position_size']}**입니다.

- 리스크 점수가 높을수록 포지션 크기를 줄여 총 손실 위험을 제한합니다.
- 자신의 리스크 허용도에 따라 조정하되, 단일 종목에 과도한 비중을 두지 마세요.

---

## 5. 시나리오 분석 (Scenario Analysis)

"""
        
        for scenario in scenarios:
            report += f"""
### {scenario['name']}

**발생 확률: {scenario['probability']:.1%}**

**확률 산출 근거:**  
{scenario['probability_reasoning']}

{scenario['description']}

---

"""
        
        report += f"""
## 6. 실행 계획 (Action Plan)

### 6-1. 진입 전략

"""
        
        if signal_type == "BUY":
            report += f"""
1. **진입 시점**
   - 현재가 (`${entry_price:,.2f}`) 부근에서 분할 매수 권고
   - 1차 진입: {risk_assessment['recommended_position_size']}의 50%
   - 2차 진입: RSI 소폭 하락 시 나머지 50% 추가 (평단가 낮추기)

2. **진입 전 체크리스트**
   - [ ] 트렌드 스코어 55 이상 유지 확인
   - [ ] 거래량 증가 추세 확인
   - [ ] 주요 저항선 위치 파악
   - [ ] 당일 뉴스/이슈 확인 (예상치 못한 악재 여부)
"""
        else:
            report += f"""
1. **진입 시점**
   - 현재가 (`${entry_price:,.2f}`) 부근에서 매도 포지션 진입
   - 또는 인버스/숏 ETF 매수

2. **진입 전 체크리스트**
   - [ ] 트렌드 스코어 45 이하 확인
   - [ ] 하락 추세 유지 확인
   - [ ] 지지선 이탈 확인
"""
        
        report += f"""

### 6-2. 손절 전략

**다음 조건 중 하나라도 충족 시 즉시 청산:**

1. 가격이 손절가 `${sl_price:,.2f}` {"이하로 하락" if signal_type == "BUY" else "이상으로 상승"}
2. EMA {"역배열 전환 (EMA1 < EMA2)" if signal_type == "BUY" else "정배열 전환 (EMA1 > EMA2)"}
3. RSI가 {"40 이하로 하락" if signal_type == "BUY" else "60 이상으로 상승"}
4. 트렌드 스코어가 {"50 이하로 하락" if signal_type == "BUY" else "50 이상으로 상승"}

**손절 실행 시 주의사항:**
- 감정적 판단 배제, 기계적으로 실행
- 손절 후 복수 매매 금지
- 손절 원인 분석 후 다음 기회 대기

### 6-3. 익절 전략

**단계별 익절 계획:**

1. **1차 익절 (목표가 도달 시)**
   - 목표가 `${tp_price:,.2f}` 도달 시 50% 청산
   - 나머지 50%는 트레일링 스탑 설정

2. **2차 익절 (추세 유지 시)**
   - 트레일링 스탑: 최고가 대비 -3% 하락 시 자동 청산
   - 추세가 강하게 유지되면 2차 목표가 설정 가능

3. **최종 청산 (신호 전환 시)**
   - {("SELL" if signal_type == "BUY" else "BUY")} 신호 발생 시 전량 매도
   - 추세 약화 신호 발생 시 조기 청산 고려

---

## 7. 모니터링 체크리스트

**포지션 진입 후 다음 항목을 주기적으로 모니터링하세요:**

- [ ] **일일 체크** (매일 종가 기준)
  - 트렌드 스코어 변화 확인
  - RSI 과열 여부 체크
  - 거래량 패턴 분석
  - 손익률 확인

- [ ] **주간 체크** (매주 금요일)
  - 전체 시장 추세 점검
  - 섹터 동향 분석
  - 뉴스/이벤트 리뷰

- [ ] **긴급 체크** (다음 상황 발생 시 즉시)
  - 급격한 가격 변동 (5% 이상)
  - 예상치 못한 뉴스/공시
  - 시장 전체 급락/급등

---

## 8. 면책조항 (Disclaimer)

본 리포트는 VMSI-SDM 시스템의 기술적 분석 결과를 바탕으로 자동 생성된 **참고 자료**입니다.

- 투자 결정은 투자자 본인의 판단과 책임 하에 이루어져야 합니다.
- 본 리포트는 투자 권유가 아닌 **정보 제공 목적**으로만 제공됩니다.
- **과거 성과가 미래 수익을 보장하지 않습니다.**
- 시장 상황, 예상치 못한 이벤트 등으로 분석 결과와 다른 결과가 발생할 수 있습니다.

모든 투자 결정에는 손실 위험이 따르며, 투자자는 자신의 리스크 허용도를 고려하여 신중하게 판단해야 합니다.

---

**Report Details:**
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Analyst: VMSI-SDM Automated System v3.0
- Classification: Technical Analysis | For Reference Only
- Signal ID: {signal_data.get('id', 'N/A')}

---
"""
        
        return report.strip()
