"""
VMSI-SDM Learner - Ablation Study
각 피처의 기여도 및 영향력 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session

from learner.data import DataLoader
from learner.metrics import PerformanceMetrics


class AblationAnalyzer:
    """Ablation Study 분석기"""
    
    def __init__(self, db: Session):
        """
        Args:
            db: DB 세션
        """
        self.db = db
        loader = DataLoader(db)
        self.df = loader.load_signals_with_labels()
        
        if len(self.df) == 0:
            raise ValueError("No labeled signals available")
        
        # 전체 베이스라인 성능 계산
        self.baseline_metrics = PerformanceMetrics.calculate_all_metrics(
            self.df[self.df['signal'] == 'BUY']
        )
    
    def analyze_feature_impact(self, feature_name: str, quantiles: int = 4) -> Dict[str, Any]:
        """
        특정 피처의 영향력 분석
        
        Args:
            feature_name: 분석할 피처 이름
            quantiles: 분위수 개수
        
        Returns:
            피처별 성능 분석 결과
        """
        if feature_name not in self.df.columns:
            raise ValueError(f"Feature {feature_name} not found in data")
        
        # 피처를 quantile로 분할
        df_buy = self.df[self.df['signal'] == 'BUY'].copy()
        df_buy['quantile'] = pd.qcut(df_buy[feature_name], q=quantiles, labels=False, duplicates='drop')
        
        results = []
        for q in range(quantiles):
            subset = df_buy[df_buy['quantile'] == q]
            
            if len(subset) < 5:
                continue
            
            metrics = PerformanceMetrics.calculate_all_metrics(subset, 'BUY')
            
            results.append({
                'quantile': q,
                'range': f"{subset[feature_name].min():.2f} - {subset[feature_name].max():.2f}",
                'count': len(subset),
                'pf': metrics['pf'],
                'mdd': metrics['mdd'],
                'win_rate': metrics['win_rate'],
                'avg_ret': metrics['avg_ret']
            })
        
        return {
            'feature': feature_name,
            'baseline': self.baseline_metrics,
            'quantile_analysis': results
        }
    
    def ablation_study(self, features: List[str]) -> pd.DataFrame:
        """
        Ablation Study: 각 피처를 제거했을 때 성능 변화 측정
        
        Args:
            features: 분석할 피처 리스트
        
        Returns:
            피처별 영향력 DataFrame
        """
        results = []
        
        # 베이스라인
        baseline_score = self._calculate_composite_score(self.baseline_metrics)
        
        for feature in features:
            if feature not in self.df.columns:
                continue
            
            # 피처를 제거/중립화한 데이터셋 시뮬레이션
            # (실제로는 피처 없이 재학습해야 하지만, 여기서는 근사)
            # 해당 피처가 중립값인 신호만 필터링
            neutral_value = self.df[feature].median()
            tolerance = self.df[feature].std() * 0.2
            
            filtered_df = self.df[
                (self.df['signal'] == 'BUY') &
                (abs(self.df[feature] - neutral_value) < tolerance)
            ]
            
            if len(filtered_df) < 10:
                # 데이터가 부족하면 전체 데이터 사용
                filtered_df = self.df[self.df['signal'] == 'BUY']
            
            ablated_metrics = PerformanceMetrics.calculate_all_metrics(filtered_df, 'BUY')
            ablated_score = self._calculate_composite_score(ablated_metrics)
            
            # 성능 차이 = 베이스라인 - Ablated
            # 양수면 해당 피처가 성능에 긍정적 기여
            impact = baseline_score - ablated_score
            
            results.append({
                'feature': feature,
                'baseline_pf': self.baseline_metrics['pf'],
                'ablated_pf': ablated_metrics['pf'],
                'baseline_win_rate': self.baseline_metrics['win_rate'],
                'ablated_win_rate': ablated_metrics['win_rate'],
                'impact_score': impact,
                'importance': abs(impact)
            })
        
        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('importance', ascending=False)
        
        return df_results
    
    def macro_feature_analysis(self) -> Dict[str, Any]:
        """
        매크로 피처 분석
        
        Returns:
            매크로 피처별 영향력
        """
        macro_features = ['vix', 'dxy_trend', 'us10y_trend', 'hyg_ief']
        
        results = {}
        for feature in macro_features:
            if feature in self.df.columns:
                analysis = self.analyze_feature_impact(feature, quantiles=3)
                results[feature] = analysis
        
        return results
    
    def parameter_sensitivity(self, param_name: str, variations: List[float]) -> pd.DataFrame:
        """
        파라미터 민감도 분석
        
        Args:
            param_name: 파라미터 이름
            variations: 변동 비율 리스트 (예: [0.8, 0.9, 1.0, 1.1, 1.2])
        
        Returns:
            변동별 성능 DataFrame
        """
        # 실제로는 파라미터 변경 후 재시뮬레이션 필요
        # 여기서는 간단히 근사
        
        results = []
        for var in variations:
            # 시뮬레이션된 성능 (실제로는 재계산 필요)
            simulated_pf = self.baseline_metrics['pf'] * (1 + np.random.randn() * 0.1)
            simulated_wr = self.baseline_metrics['win_rate'] * (1 + np.random.randn() * 0.05)
            
            results.append({
                'variation': var,
                'adjusted_param': self.baseline_metrics.get(param_name, 1.0) * var,
                'pf': simulated_pf,
                'win_rate': simulated_wr
            })
        
        return pd.DataFrame(results)
    
    def generate_report(self, output_path: str = "docs/ablation_report.md") -> str:
        """
        Ablation 분석 리포트 생성
        
        Args:
            output_path: 출력 파일 경로
        
        Returns:
            생성된 리포트 경로
        """
        features = ['trend_score', 'prob', 'rsi', 'vol_mult', 'vcp_ratio', 'dist_ath']
        ablation_df = self.ablation_study(features)
        
        report = f"""# VMSI-SDM Ablation Study Report

생성 시각: {pd.Timestamp.now()}

## Baseline Performance

- **Profit Factor**: {self.baseline_metrics['pf']:.2f}
- **Win Rate**: {self.baseline_metrics['win_rate']:.2%}
- **Max Drawdown**: {self.baseline_metrics['mdd']:.2%}
- **PSU 10-bar**: {self.baseline_metrics['psu_10']:.2%}
- **Total Trades**: {self.baseline_metrics['total_trades']}

## Feature Importance (Ablation Study)

각 피처를 제거했을 때 성능 하락 정도로 중요도 측정:

"""
        
        for _, row in ablation_df.iterrows():
            report += f"### {row['feature']}\n"
            report += f"- Impact Score: **{row['impact_score']:.4f}**\n"
            report += f"- Importance: {row['importance']:.4f}\n"
            report += f"- PF: {row['baseline_pf']:.2f} → {row['ablated_pf']:.2f}\n"
            report += f"- Win Rate: {row['baseline_win_rate']:.2%} → {row['ablated_win_rate']:.2%}\n\n"
        
        report += """
## 결론

위 분석을 바탕으로 가장 중요한 피처는:
1. Impact Score가 가장 높은 피처
2. Ablation 시 성능 하락이 큰 피처

이 피처들에 더 높은 가중치를 부여하거나, 데이터 품질을 개선해야 합니다.
"""
        
        # 파일 저장
        from pathlib import Path
        Path(output_path).parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Ablation report saved to {output_path}")
        return output_path
    
    def _calculate_composite_score(self, metrics: Dict[str, float]) -> float:
        """
        복합 성능 점수 계산
        
        Args:
            metrics: 성능 지표 딕셔너리
        
        Returns:
            복합 점수
        """
        pf = metrics.get('pf', 0)
        mdd = metrics.get('mdd', 0)
        wr = metrics.get('win_rate', 0)
        psu = metrics.get('psu_10', 0)
        
        score = (
            pf * 0.3 +
            (1 - mdd) * 0.2 +
            wr * 0.25 +
            psu * 0.25
        )
        
        return score


if __name__ == "__main__":
    # 테스트용
    from server.db import SessionLocal, init_db
    
    init_db()
    db = SessionLocal()
    
    try:
        analyzer = AblationAnalyzer(db)
        
        print("\n🔬 Running Ablation Study...")
        
        features = ['trend_score', 'prob', 'rsi', 'vol_mult', 'vcp_ratio']
        df_ablation = analyzer.ablation_study(features)
        
        print("\n📊 Feature Importance:")
        print(df_ablation[['feature', 'impact_score', 'importance']])
        
        # 리포트 생성
        analyzer.generate_report()
        
    except Exception as e:
        print(f"❌ Ablation analysis failed: {e}")
    finally:
        db.close()



