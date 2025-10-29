"""
VMSI-SDM Learner - Tuning Module
Optuna 기반 Bayesian Optimization
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
import optuna
from optuna.trial import Trial
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from learner.data import DataLoader
from learner.metrics import PerformanceMetrics, BacktestEngine
from server.db import Experiment


class ParameterTuner:
    """Optuna 기반 파라미터 튜너"""
    
    def __init__(
        self,
        db: Session,
        n_trials: int = 100,
        timeout: int = 3600,
        signal_type: str = 'BUY'
    ):
        """
        Args:
            db: DB 세션
            n_trials: 최적화 시도 횟수
            timeout: 최대 실행 시간 (초)
            signal_type: 최적화할 신호 타입 (BUY/SELL)
        """
        self.db = db
        self.n_trials = n_trials
        self.timeout = timeout
        self.signal_type = signal_type
        
        # 데이터 로드
        loader = DataLoader(db)
        df = loader.load_signals_with_labels()
        
        if len(df) == 0:
            raise ValueError("No labeled signals available. Run labeler first.")
        
        self.train_df, self.test_df = loader.split_walk_forward(df, train_ratio=0.7)
        print(f"✓ Loaded data: Train={len(self.train_df)}, Test={len(self.test_df)}")
    
    def objective(self, trial: Trial) -> float:
        """
        Optuna 목적 함수
        
        Args:
            trial: Optuna Trial 객체
        
        Returns:
            최적화할 목표값 (높을수록 좋음)
        """
        # 파라미터 제안
        params = {
            'rsi_buy_th': trial.suggest_float('rsi_buy_th', 50, 70),
            'rsi_sell_th': trial.suggest_float('rsi_sell_th', 30, 50),
            'vol_mult_buy': trial.suggest_float('vol_mult_buy', 1.0, 3.0),
            'vol_mult_sell': trial.suggest_float('vol_mult_sell', 1.0, 3.0),
            'vcp_ratio_th': trial.suggest_float('vcp_ratio_th', 0.1, 0.8),
            'dist_ath_max': trial.suggest_float('dist_ath_max', 0.05, 0.3),
            'alpha': trial.suggest_float('alpha', 0.5, 1.0),
            'beta': trial.suggest_float('beta', 0.1, 0.6),
            'gamma': trial.suggest_float('gamma', 0.3, 1.0),
            'delta': trial.suggest_float('delta', 0.2, 0.8),
            'epsilon': trial.suggest_float('epsilon', 0.5, 1.0),
            'hysteresis_len': trial.suggest_int('hysteresis_len', 2, 5),
            'cooldown_bars': trial.suggest_int('cooldown_bars', 2, 5),
            # 매크로 가중치
            'vix_w': trial.suggest_float('vix_w', -0.5, 0.0),
            'dxy_w': trial.suggest_float('dxy_w', -0.5, 0.0),
            'us10y_w': trial.suggest_float('us10y_w', -0.5, 0.0),
            'hygief_w': trial.suggest_float('hygief_w', 0.0, 0.6),
        }
        
        # 파라미터 적용한 시뮬레이션 (간단화)
        # 실제로는 이 파라미터로 신호를 재생성해야 하지만,
        # 여기서는 기존 신호 중 필터링으로 근사
        filtered_df = self._apply_filters(self.train_df, params)
        
        if len(filtered_df) < 10:
            # 신호가 너무 적으면 패널티
            return 0.0
        
        # 성능 지표 계산
        metrics = PerformanceMetrics.calculate_all_metrics(filtered_df, self.signal_type)
        
        # 목표: Profit Factor 최대화, MDD 최소화, PSU 정확도 최대화
        pf = metrics['pf']
        mdd = metrics['mdd']
        psu_10 = metrics['psu_10']
        win_rate = metrics['win_rate']
        
        # 복합 목표 함수
        # PF > 1.5, MDD < 0.2, PSU > 0.6 목표
        score = (
            pf * 0.4 +
            (1 - mdd) * 0.2 +
            psu_10 * 0.3 +
            win_rate * 0.1
        )
        
        return score
    
    def _apply_filters(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        파라미터 기반 필터 적용 (시뮬레이션)
        
        Args:
            df: 원본 DataFrame
            params: 파라미터 딕셔너리
        
        Returns:
            필터링된 DataFrame
        """
        filtered = df[df['signal'] == self.signal_type].copy()
        
        # RSI 필터
        if self.signal_type == 'BUY':
            filtered = filtered[filtered['rsi'] > params['rsi_buy_th']]
        else:
            filtered = filtered[filtered['rsi'] < params['rsi_sell_th']]
        
        # Volume 필터
        if self.signal_type == 'BUY':
            filtered = filtered[filtered['vol_mult'] > params['vol_mult_buy']]
        else:
            filtered = filtered[filtered['vol_mult'] > params['vol_mult_sell']]
        
        # VCP 필터
        filtered = filtered[filtered['vcp_ratio'] < params['vcp_ratio_th']]
        
        # ATH 거리 필터
        filtered = filtered[filtered['dist_ath'] < params['dist_ath_max']]
        
        return filtered
    
    def optimize(self) -> Dict[str, Any]:
        """
        최적화 실행
        
        Returns:
            최적 파라미터 및 성능 지표
        """
        print(f"\n🔄 Starting optimization for {self.signal_type} signals...")
        print(f"   Trials: {self.n_trials}, Timeout: {self.timeout}s")
        
        study = optuna.create_study(
            direction='maximize',
            sampler=optuna.samplers.TPESampler(seed=42)
        )
        
        study.optimize(
            self.objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True
        )
        
        best_params = study.best_params
        best_value = study.best_value
        
        print(f"\n✓ Optimization complete!")
        print(f"   Best score: {best_value:.4f}")
        print(f"   Best params: {best_params}")
        
        # 테스트 세트에서 검증
        test_filtered = self._apply_filters(self.test_df, best_params)
        test_metrics = PerformanceMetrics.calculate_all_metrics(test_filtered, self.signal_type)
        
        print(f"\n📊 Test Set Performance:")
        print(f"   - Profit Factor: {test_metrics['pf']:.2f}")
        print(f"   - Max Drawdown: {test_metrics['mdd']:.2%}")
        print(f"   - Win Rate: {test_metrics['win_rate']:.2%}")
        print(f"   - PSU 10-bar: {test_metrics['psu_10']:.2%}")
        
        # 결과 저장
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        experiment = Experiment(
            run_id=run_id,
            params=best_params,
            metrics=test_metrics
        )
        self.db.add(experiment)
        self.db.commit()
        
        return {
            'run_id': run_id,
            'params': best_params,
            'train_score': best_value,
            'test_metrics': test_metrics
        }


def run_optimization(
    db: Session,
    signal_type: str = 'BUY',
    n_trials: int = 100,
    timeout: int = 3600
) -> Dict[str, Any]:
    """
    최적화 실행 (편의 함수)
    
    Args:
        db: DB 세션
        signal_type: BUY 또는 SELL
        n_trials: 시도 횟수
        timeout: 타임아웃 (초)
    
    Returns:
        최적화 결과
    """
    tuner = ParameterTuner(db, n_trials=n_trials, timeout=timeout, signal_type=signal_type)
    result = tuner.optimize()
    
    return result


if __name__ == "__main__":
    import argparse
    from server.db import SessionLocal, init_db
    from learner.preset import PresetManager
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='VMSI-SDM Optuna Learning Loop')
    parser.add_argument('--signal-type', type=str, default='BUY', choices=['BUY', 'SELL'],
                        help='Signal type to optimize (default: BUY)')
    parser.add_argument('--trials', type=int, default=50,
                        help='Number of optimization trials (default: 50)')
    parser.add_argument('--timeout', type=int, default=3600,
                        help='Timeout in seconds (default: 3600)')
    parser.add_argument('--save-preset', action='store_true',
                        help='Save best parameters to preset_B_candidate.json')
    
    args = parser.parse_args()
    
    print("[INFO] Starting VMSI-SDM Optuna Learning Loop")
    print(f"[INFO] Signal Type: {args.signal_type}")
    print(f"[INFO] Trials: {args.trials}")
    print(f"[INFO] Timeout: {args.timeout}s")
    
    # DB 초기화 (클라우드 환경에서는 이미 초기화되어 있을 수 있음)
    try:
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARN] Database init skipped: {e}")
    
    db = SessionLocal()
    
    try:
        result = run_optimization(
            db, 
            signal_type=args.signal_type, 
            n_trials=args.trials, 
            timeout=args.timeout
        )
        
        print("\n[OK] Optimization result saved to database")
        
        # preset_B_candidate.json 저장 (선택사항)
        if args.save_preset:
            preset_mgr = PresetManager()
            best_params = result['params']
            
            # Pine Script 형식으로 변환 (선택적)
            pine_params = {
                'ema1_len': 20,  # 고정값
                'ema2_len': 50,  # 고정값
                'rsi_len': 14,   # 고정값
                'vcp_len': 50,   # 고정값
                'alpha': best_params['alpha'],
                'beta': best_params['beta'],
                'gamma': best_params['gamma'],
                'delta': best_params['delta'],
                'epsilon': best_params['epsilon'],
                'hysteresis_len': best_params['hysteresis_len'],
                'cooldown_bars': best_params['cooldown_bars'],
            }
            
            preset_mgr.save_preset('preset_B_candidate', pine_params)
            print("[OK] Best parameters saved to preset_B_candidate.json")
        
        print(f"\n[SUMMARY]")
        print(f"  Run ID: {result['run_id']}")
        print(f"  Train Score: {result['train_score']:.4f}")
        print(f"  Test Metrics: PF={result['test_metrics']['pf']:.2f}, "
              f"Win%={result['test_metrics']['win_rate']:.1%}, "
              f"MDD={result['test_metrics']['mdd']:.1%}")
        
    except ValueError as e:
        print(f"[ERROR] No data available: {e}")
        print("[INFO] Make sure signals are collected from TradingView first")
        exit(1)
    except Exception as e:
        print(f"[ERROR] Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    finally:
        db.close()
        print("[INFO] Database connection closed")

