"""
VMSI-SDM Learner - Data Module
학습용 데이터 로드 및 전처리
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from server.db import Signal, Label


class DataLoader:
    """학습 데이터 로더"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def load_signals_with_labels(self, min_labels: int = 4) -> pd.DataFrame:
        """
        라벨이 있는 신호들을 DataFrame으로 로드
        
        Args:
            min_labels: 최소 라벨 개수 (기본 4: 3, 5, 10, 20봉)
        
        Returns:
            신호 + 라벨이 결합된 DataFrame
        """
        # 라벨이 충분한 신호들만 조회
        signals = self.db.query(Signal).all()
        
        data = []
        for signal in signals:
            labels = {label.fwd_n: label for label in signal.labels}
            
            # 라벨이 충분하지 않으면 스킵
            if len(labels) < min_labels:
                continue
            
            # 피처 추출
            features = signal.features_json
            params = signal.params_json
            
            row = {
                'signal_id': signal.id,
                'symbol': signal.symbol,
                'tf': signal.tf,
                'signal': signal.signal,
                'ts': signal.ts,
                # 피처
                'trend_score': features.get('trendScore', 0),
                'prob': features.get('prob', 0),
                'ema20_above_50': features.get('ema20_above_50', False),
                'rsi': features.get('rsi', 50),
                'vol_mult': features.get('vol_mult', 1),
                'vcp_ratio': features.get('vcp_ratio', 0),
                'dist_ath': features.get('dist_ath', 0),
                # 매크로
                'vix': features.get('macro', {}).get('vix', 18),
                'dxy_trend': features.get('macro', {}).get('dxy_trend', 'flat'),
                'us10y_trend': features.get('macro', {}).get('us10y_trend', 'flat'),
                'hyg_ief': features.get('macro', {}).get('hyg_ief', 'bull'),
                # 파라미터
                'alpha': params.get('alpha', 0.8),
                'beta': params.get('beta', 0.35),
                'gamma': params.get('gamma', 0.7),
                'delta': params.get('delta', 0.6),
                'epsilon': params.get('epsilon', 0.8),
                # 라벨
                'fwd_ret_3': labels.get(3).fwd_ret if 3 in labels else 0,
                'fwd_ret_5': labels.get(5).fwd_ret if 5 in labels else 0,
                'fwd_ret_10': labels.get(10).fwd_ret if 10 in labels else 0,
                'fwd_ret_20': labels.get(20).fwd_ret if 20 in labels else 0,
                'broke_high_10': labels.get(10).broke_high if 10 in labels else False,
                'broke_low_10': labels.get(10).broke_low if 10 in labels else False,
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        return df
    
    def split_walk_forward(self, df: pd.DataFrame, train_ratio: float = 0.7) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        워크포워드 방식으로 데이터 분할
        
        Args:
            df: 전체 데이터
            train_ratio: 학습 데이터 비율
        
        Returns:
            (train_df, test_df)
        """
        # 시간순 정렬
        df = df.sort_values('ts').reset_index(drop=True)
        
        split_idx = int(len(df) * train_ratio)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        return train_df, test_df
    
    def get_signal_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        신호 통계 계산
        
        Args:
            df: 신호 DataFrame
        
        Returns:
            통계 딕셔너리
        """
        stats = {
            'total_signals': len(df),
            'buy_signals': len(df[df['signal'] == 'BUY']),
            'sell_signals': len(df[df['signal'] == 'SELL']),
            'avg_trend_score': df['trend_score'].mean(),
            'avg_prob': df['prob'].mean(),
            'avg_rsi': df['rsi'].mean(),
            'avg_fwd_ret_10': df['fwd_ret_10'].mean(),
            'win_rate_10': (df['fwd_ret_10'] > 0).mean() if len(df) > 0 else 0,
        }
        return stats
    
    def filter_by_signal_type(self, df: pd.DataFrame, signal_type: str) -> pd.DataFrame:
        """
        신호 타입으로 필터링
        
        Args:
            df: 전체 데이터
            signal_type: BUY, SELL, WATCH_UP, WATCH_DOWN
        
        Returns:
            필터링된 DataFrame
        """
        return df[df['signal'] == signal_type].copy()


def prepare_training_data(db: Session) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    학습용 데이터 준비 (편의 함수)
    
    Args:
        db: DB 세션
    
    Returns:
        (train_df, test_df)
    """
    loader = DataLoader(db)
    df = loader.load_signals_with_labels()
    
    if len(df) == 0:
        print("⚠️  No labeled signals found. Please run labeler first.")
        return pd.DataFrame(), pd.DataFrame()
    
    train_df, test_df = loader.split_walk_forward(df, train_ratio=0.7)
    
    print(f"✓ Loaded {len(df)} signals")
    print(f"  - Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
    print(f"  - Test: {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")
    
    return train_df, test_df


if __name__ == "__main__":
    # 테스트용
    from server.db import SessionLocal, init_db
    
    init_db()
    db = SessionLocal()
    
    loader = DataLoader(db)
    df = loader.load_signals_with_labels()
    
    if len(df) > 0:
        print("\n📊 Signal Statistics:")
        stats = loader.get_signal_stats(df)
        for key, value in stats.items():
            print(f"  - {key}: {value}")
    else:
        print("⚠️  No data available")
    
    db.close()



