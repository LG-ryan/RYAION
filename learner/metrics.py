"""
VMSI-SDM Learner - Metrics Module
성능 평가 지표 계산
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class PerformanceMetrics:
    """성능 지표 계산기"""
    
    @staticmethod
    def profit_factor(returns: pd.Series) -> float:
        """
        Profit Factor 계산
        PF = sum(positive returns) / abs(sum(negative returns))
        
        Args:
            returns: 수익률 시리즈
        
        Returns:
            Profit Factor
        """
        positive = returns[returns > 0].sum()
        negative = abs(returns[returns < 0].sum())
        
        if negative == 0:
            return float('inf') if positive > 0 else 0.0
        
        return positive / negative
    
    @staticmethod
    def max_drawdown(returns: pd.Series) -> float:
        """
        Maximum Drawdown 계산
        
        Args:
            returns: 수익률 시리즈
        
        Returns:
            MDD (0~1)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        
        return abs(drawdown.min())
    
    @staticmethod
    def win_rate(returns: pd.Series) -> float:
        """
        승률 계산
        
        Args:
            returns: 수익률 시리즈
        
        Returns:
            승률 (0~1)
        """
        if len(returns) == 0:
            return 0.0
        return (returns > 0).sum() / len(returns)
    
    @staticmethod
    def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Sharpe Ratio 계산 (연환산)
        
        Args:
            returns: 수익률 시리즈
            risk_free_rate: 무위험 수익률
        
        Returns:
            Sharpe Ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    @staticmethod
    def signal_accuracy(df: pd.DataFrame, signal_type: str = 'BUY', threshold: float = 0.02) -> Dict[str, float]:
        """
        신호 정확도 계산
        
        Args:
            df: 신호 + 라벨 DataFrame
            signal_type: BUY 또는 SELL
            threshold: 성공 기준 수익률
        
        Returns:
            {'psu_3', 'psu_5', 'psu_10', 'psu_20'} 정확도 딕셔너리
        """
        signal_df = df[df['signal'] == signal_type]
        
        if len(signal_df) == 0:
            return {'psu_3': 0, 'psu_5': 0, 'psu_10': 0, 'psu_20': 0}
        
        accuracy = {}
        for n in [3, 5, 10, 20]:
            col = f'fwd_ret_{n}'
            if col in signal_df.columns:
                if signal_type == 'BUY':
                    # BUY: 수익률 > threshold
                    success = (signal_df[col] > threshold).sum()
                else:
                    # SELL: 수익률 < -threshold
                    success = (signal_df[col] < -threshold).sum()
                
                accuracy[f'psu_{n}'] = success / len(signal_df)
            else:
                accuracy[f'psu_{n}'] = 0
        
        return accuracy
    
    @staticmethod
    def calculate_all_metrics(df: pd.DataFrame, signal_type: str = 'BUY') -> Dict[str, float]:
        """
        모든 성능 지표 한 번에 계산
        
        Args:
            df: 신호 + 라벨 DataFrame
            signal_type: BUY 또는 SELL
        
        Returns:
            전체 성능 지표 딕셔너리
        """
        signal_df = df[df['signal'] == signal_type]
        
        if len(signal_df) == 0:
            return {
                'pf': 0, 'mdd': 0, 'win_rate': 0, 'sharpe': 0,
                'psu_3': 0, 'psu_5': 0, 'psu_10': 0, 'psu_20': 0,
                'avg_ret': 0, 'total_trades': 0
            }
        
        # 10봉 후 수익률 기준
        returns = signal_df['fwd_ret_10']
        
        metrics = {
            'pf': PerformanceMetrics.profit_factor(returns),
            'mdd': PerformanceMetrics.max_drawdown(returns),
            'win_rate': PerformanceMetrics.win_rate(returns),
            'sharpe': PerformanceMetrics.sharpe_ratio(returns),
            'avg_ret': returns.mean(),
            'total_trades': len(signal_df)
        }
        
        # 신호 정확도 추가
        accuracy = PerformanceMetrics.signal_accuracy(df, signal_type)
        metrics.update(accuracy)
        
        return metrics
    
    @staticmethod
    def stability_score(df: pd.DataFrame, param_name: str, variation: float = 0.2) -> float:
        """
        파라미터 안정성 점수 계산
        파라미터를 ±variation 만큼 변경했을 때 성능 변화 측정
        
        Args:
            df: 신호 + 라벨 DataFrame
            param_name: 파라미터 이름
            variation: 변동 폭 (기본 20%)
        
        Returns:
            안정성 점수 (0~1, 높을수록 안정적)
        """
        # 실제로는 시뮬레이션 필요, 여기서는 간단히 근사
        # 실제 구현 시 파라미터 변경 후 재계산
        return 0.85  # 임시값


class BacktestEngine:
    """간단한 백테스트 엔진"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
    
    def run(self, df: pd.DataFrame, signal_type: str = 'BUY') -> Dict[str, float]:
        """
        백테스트 실행
        
        Args:
            df: 신호 + 라벨 DataFrame
            signal_type: 신호 타입
        
        Returns:
            백테스트 결과
        """
        signal_df = df[df['signal'] == signal_type].sort_values('ts')
        
        if len(signal_df) == 0:
            return {'final_capital': self.initial_capital, 'total_return': 0, 'num_trades': 0}
        
        capital = self.initial_capital
        returns_series = []
        
        for _, row in signal_df.iterrows():
            ret = row['fwd_ret_10']
            capital *= (1 + ret)
            returns_series.append(ret)
        
        returns_series = pd.Series(returns_series)
        
        result = {
            'final_capital': capital,
            'total_return': (capital - self.initial_capital) / self.initial_capital,
            'num_trades': len(signal_df),
            'pf': PerformanceMetrics.profit_factor(returns_series),
            'mdd': PerformanceMetrics.max_drawdown(returns_series),
            'win_rate': PerformanceMetrics.win_rate(returns_series),
            'sharpe': PerformanceMetrics.sharpe_ratio(returns_series),
            'avg_ret': returns_series.mean()
        }
        
        return result


if __name__ == "__main__":
    # 테스트용
    # 가상의 수익률 데이터
    np.random.seed(42)
    returns = pd.Series(np.random.randn(100) * 0.02 + 0.005)
    
    print("📊 Performance Metrics Test:")
    print(f"  - Profit Factor: {PerformanceMetrics.profit_factor(returns):.2f}")
    print(f"  - Max Drawdown: {PerformanceMetrics.max_drawdown(returns):.2%}")
    print(f"  - Win Rate: {PerformanceMetrics.win_rate(returns):.2%}")
    print(f"  - Sharpe Ratio: {PerformanceMetrics.sharpe_ratio(returns):.2f}")


