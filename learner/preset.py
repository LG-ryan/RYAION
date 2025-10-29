"""
VMSI-SDM Learner - Preset Manager
프리셋 JSON 생성 및 관리
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class PresetManager:
    """프리셋 관리자"""
    
    def __init__(self, preset_dir: str = "presets"):
        """
        Args:
            preset_dir: 프리셋 저장 디렉토리
        """
        self.preset_dir = Path(preset_dir)
        self.preset_dir.mkdir(exist_ok=True)
        
        self.current_preset_path = self.preset_dir / "preset_A_current.json"
        self.candidate_preset_path = self.preset_dir / "preset_B_candidate.json"
    
    def create_preset(
        self,
        params: Dict[str, Any],
        metrics: Dict[str, float],
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        프리셋 생성
        
        Args:
            params: 파라미터 딕셔너리
            metrics: 성능 지표 딕셔너리
            version: 버전 문자열 (없으면 자동 생성)
        
        Returns:
            프리셋 딕셔너리
        """
        if version is None:
            version = f"v{datetime.now().strftime('%Y-%m-%d_%H%M')}"
        
        # Pine Script 파라미터로 변환
        pine_params = {
            "ema1": params.get("ema1", 20),
            "ema2": params.get("ema2", 50),
            "rsi": params.get("rsi", 14),
            "vcp": params.get("vcp", 20),
            "rsi_buy_th": params.get("rsi_buy_th", 55),
            "rsi_sell_th": params.get("rsi_sell_th", 45),
            "vol_mult_buy": params.get("vol_mult_buy", 1.5),
            "vol_mult_sell": params.get("vol_mult_sell", 1.3),
            "macro_weights": {
                "vix_w": params.get("vix_w", -0.3),
                "dxy_w": params.get("dxy_w", -0.2),
                "us10y_w": params.get("us10y_w", -0.2),
                "hygief_w": params.get("hygief_w", 0.4)
            },
            "alpha": params.get("alpha", 0.8),
            "beta": params.get("beta", 0.35),
            "gamma": params.get("gamma", 0.7),
            "delta": params.get("delta", 0.6),
            "epsilon": params.get("epsilon", 0.8),
            "hysteresis_len": params.get("hysteresis_len", 3),
            "cooldown_bars": params.get("cooldown_bars", 3)
        }
        
        preset = {
            "version": version,
            "created_at": datetime.now().isoformat(),
            "params": pine_params,
            "metrics": {
                "pf": round(metrics.get("pf", 0), 2),
                "mdd": round(metrics.get("mdd", 0), 4),
                "psu_success": round(metrics.get("psu_10", 0), 2),
                "win_rate": round(metrics.get("win_rate", 0), 2),
                "total_trades": metrics.get("total_trades", 0)
            }
        }
        
        return preset
    
    def save_preset(self, preset: Dict[str, Any], path: Optional[Path] = None) -> str:
        """
        프리셋을 파일로 저장
        
        Args:
            preset: 프리셋 딕셔너리
            path: 저장 경로 (없으면 candidate로 저장)
        
        Returns:
            저장된 파일 경로
        """
        if path is None:
            path = self.candidate_preset_path
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(preset, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Preset saved to {path}")
        return str(path)
    
    def load_preset(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """
        프리셋 파일 로드
        
        Args:
            path: 로드할 경로 (없으면 current 로드)
        
        Returns:
            프리셋 딕셔너리
        """
        if path is None:
            path = self.current_preset_path
        
        if not path.exists():
            print(f"⚠️  Preset file not found: {path}")
            return self._get_default_preset()
        
        with open(path, 'r', encoding='utf-8') as f:
            preset = json.load(f)
        
        return preset
    
    def promote_candidate_to_current(self) -> bool:
        """
        후보 프리셋을 현재 프리셋으로 승격
        
        Returns:
            성공 여부
        """
        if not self.candidate_preset_path.exists():
            print("⚠️  No candidate preset found")
            return False
        
        # 기존 current 백업
        if self.current_preset_path.exists():
            backup_path = self.preset_dir / f"preset_A_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.current_preset_path.rename(backup_path)
            print(f"✓ Backed up current preset to {backup_path}")
        
        # Candidate를 Current로 복사
        candidate = self.load_preset(self.candidate_preset_path)
        self.save_preset(candidate, self.current_preset_path)
        
        print(f"✓ Promoted candidate to current preset")
        return True
    
    def compare_presets(self) -> Dict[str, Any]:
        """
        현재 프리셋과 후보 프리셋 비교
        
        Returns:
            비교 결과 딕셔너리
        """
        current = self.load_preset(self.current_preset_path)
        candidate = self.load_preset(self.candidate_preset_path)
        
        comparison = {
            "current": current,
            "candidate": candidate,
            "metrics_diff": {}
        }
        
        # 성능 지표 비교
        for key in ["pf", "mdd", "psu_success", "win_rate"]:
            current_val = current.get("metrics", {}).get(key, 0)
            candidate_val = candidate.get("metrics", {}).get(key, 0)
            comparison["metrics_diff"][key] = {
                "current": current_val,
                "candidate": candidate_val,
                "diff": candidate_val - current_val,
                "improvement": ((candidate_val - current_val) / current_val * 100) if current_val != 0 else 0
            }
        
        return comparison
    
    def generate_pine_script_comment(self, preset: Dict[str, Any]) -> str:
        """
        Pine Script에 복사-붙여넣기할 주석 생성
        
        Args:
            preset: 프리셋 딕셔너리
        
        Returns:
            Pine Script 주석 문자열
        """
        params = preset["params"]
        metrics = preset["metrics"]
        
        script = f"""
// @preset {preset['version']}
// Generated: {preset['created_at']}
// Metrics: PF={metrics['pf']}, MDD={metrics['mdd']:.2%}, WinRate={metrics['win_rate']:.2%}

// 파라미터 설정
ema1_len = {params['ema1']}
ema2_len = {params['ema2']}
rsi_len = {params['rsi']}
vcp_len = {params['vcp']}

rsi_buy_th = {params['rsi_buy_th']}
rsi_sell_th = {params['rsi_sell_th']}
vol_mult_buy = {params['vol_mult_buy']}
vol_mult_sell = {params['vol_mult_sell']}

alpha = {params['alpha']}
beta = {params['beta']}
gamma = {params['gamma']}
delta = {params['delta']}
epsilon = {params['epsilon']}

hysteresis_len = {params['hysteresis_len']}
cooldown_bars = {params['cooldown_bars']}

vix_w = {params['macro_weights']['vix_w']}
dxy_w = {params['macro_weights']['dxy_w']}
us10y_w = {params['macro_weights']['us10y_w']}
hygief_w = {params['macro_weights']['hygief_w']}
"""
        return script.strip()
    
    def _get_default_preset(self) -> Dict[str, Any]:
        """기본 프리셋 반환"""
        return {
            "version": "v2025-10-29_default",
            "created_at": datetime.now().isoformat(),
            "params": {
                "ema1": 20,
                "ema2": 50,
                "rsi": 14,
                "vcp": 20,
                "rsi_buy_th": 55,
                "rsi_sell_th": 45,
                "vol_mult_buy": 1.5,
                "vol_mult_sell": 1.3,
                "macro_weights": {
                    "vix_w": -0.3,
                    "dxy_w": -0.2,
                    "us10y_w": -0.2,
                    "hygief_w": 0.4
                },
                "alpha": 0.8,
                "beta": 0.35,
                "gamma": 0.7,
                "delta": 0.6,
                "epsilon": 0.8,
                "hysteresis_len": 3,
                "cooldown_bars": 3
            },
            "metrics": {
                "pf": 1.47,
                "mdd": 0.14,
                "psu_success": 0.68,
                "win_rate": 0.62,
                "total_trades": 0
            }
        }


if __name__ == "__main__":
    # 테스트용
    manager = PresetManager()
    
    # 기본 프리셋 생성
    default_preset = manager._get_default_preset()
    manager.save_preset(default_preset, manager.current_preset_path)
    
    print("✓ Default preset created")
    print("\n" + manager.generate_pine_script_comment(default_preset))



