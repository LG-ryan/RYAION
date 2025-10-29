"""
실제 백테스트와 유사한 샘플 데이터 생성
SPX 최근 3년 데이터 기반
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import requests
import time

# 상위 디렉토리 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

# FastAPI 서버 URL
API_URL = "http://localhost:8000/alert"

def generate_realistic_signals():
    """실제 SPX 추세를 반영한 신호 생성"""
    
    signals = []
    
    # 실제 SPX 주요 이벤트 반영 (2022-10-29 ~ 2025-10-29)
    periods = [
        # 2022 Q4: 저점에서 반등
        {
            "start": datetime(2022, 10, 29),
            "end": datetime(2022, 12, 31),
            "trend": "bullish",
            "base_price": 3800,
            "volatility": "high",
            "signals_count": 8
        },
        # 2023 Q1-Q2: 상승 추세
        {
            "start": datetime(2023, 1, 1),
            "end": datetime(2023, 6, 30),
            "trend": "bullish",
            "base_price": 4000,
            "volatility": "medium",
            "signals_count": 15
        },
        # 2023 Q3: 조정
        {
            "start": datetime(2023, 7, 1),
            "end": datetime(2023, 9, 30),
            "trend": "bearish",
            "base_price": 4500,
            "volatility": "medium",
            "signals_count": 6
        },
        # 2023 Q4: 강한 상승
        {
            "start": datetime(2023, 10, 1),
            "end": datetime(2023, 12, 31),
            "trend": "bullish",
            "base_price": 4400,
            "volatility": "low",
            "signals_count": 12
        },
        # 2024 Q1-Q2: 지속 상승
        {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 6, 30),
            "trend": "bullish",
            "base_price": 4800,
            "volatility": "low",
            "signals_count": 18
        },
        # 2024 Q3: 변동성 증가
        {
            "start": datetime(2024, 7, 1),
            "end": datetime(2024, 9, 30),
            "trend": "neutral",
            "base_price": 5400,
            "volatility": "high",
            "signals_count": 10
        },
        # 2024 Q4 - 2025 Q3: 신고가 행진
        {
            "start": datetime(2024, 10, 1),
            "end": datetime(2025, 10, 29),
            "trend": "bullish",
            "base_price": 5600,
            "volatility": "medium",
            "signals_count": 22
        }
    ]
    
    signal_id = 1
    
    for period in periods:
        days_in_period = (period["end"] - period["start"]).days
        interval = days_in_period // period["signals_count"]
        
        current_date = period["start"]
        current_price = period["base_price"]
        
        for i in range(period["signals_count"]):
            # 날짜 증가
            current_date += timedelta(days=interval)
            
            # 가격 변동
            if period["trend"] == "bullish":
                price_change = random.uniform(10, 50)
                current_price += price_change
                action = "BUY" if random.random() > 0.2 else "SELL"
            elif period["trend"] == "bearish":
                price_change = random.uniform(-50, -10)
                current_price += price_change
                action = "SELL" if random.random() > 0.3 else "BUY"
            else:  # neutral
                price_change = random.uniform(-30, 30)
                current_price += price_change
                action = "BUY" if random.random() > 0.5 else "SELL"
            
            # 변동성 반영
            if period["volatility"] == "high":
                atr = random.uniform(40, 80)
                vcp_ratio = random.uniform(0.05, 0.10)
            elif period["volatility"] == "medium":
                atr = random.uniform(25, 45)
                vcp_ratio = random.uniform(0.03, 0.06)
            else:  # low
                atr = random.uniform(15, 30)
                vcp_ratio = random.uniform(0.02, 0.04)
            
            # 신호 강도
            if action == "BUY":
                trend_score = random.uniform(60, 85) if period["trend"] == "bullish" else random.uniform(50, 65)
                rsi = random.uniform(52, 70)
                vol_mult = random.uniform(1.2, 2.5)
            else:
                trend_score = random.uniform(35, 50) if period["trend"] == "bearish" else random.uniform(40, 55)
                rsi = random.uniform(30, 48)
                vol_mult = random.uniform(1.2, 2.0)
            
            # SL/TP 계산 (ATR 기반)
            sl_dist = atr * 1.5 * (1 + vcp_ratio * 0.5)
            tp_dist = atr * 2.5 * (1 + vcp_ratio * 0.5)
            
            if action == "BUY":
                sl_price = current_price - sl_dist
                tp_price = current_price + tp_dist
            else:
                sl_price = current_price + sl_dist
                tp_price = current_price - tp_dist
            
            # 신호 생성
            signal = {
                "ts_unix": int(current_date.timestamp()),
                "symbol": "SPX",
                "timeframe": "1D",
                "action": action,
                "price": round(current_price, 2),
                "signal_number": signal_id,
                "trend_score": round(trend_score, 2),
                "rsi": round(rsi, 2),
                "vol_mult": round(vol_mult, 2),
                "ema1": round(current_price * 0.99, 2),
                "ema2": round(current_price * 0.98, 2),
                "sl_price": round(sl_price, 2),
                "tp_price": round(tp_price, 2),
                "atr": round(atr, 2),
                "vcp_ratio": round(vcp_ratio, 4),
                "version": "vmsi_sdm_v4_dynamic"
            }
            
            signals.append(signal)
            signal_id += 1
    
    return signals

def send_signal_to_api(signal):
    """신호를 FastAPI로 전송"""
    try:
        response = requests.post(API_URL, json=signal, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def clear_database():
    """기존 DB 삭제"""
    db_path = Path(__file__).parent.parent / "vmsi_sdm.db"
    if db_path.exists():
        try:
            os.remove(db_path)
            print(f"[OK] Deleted existing database: {db_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error deleting database: {e}")
            return False
    else:
        print("[INFO] No existing database found")
        return True

def main():
    print("=" * 70)
    print("Realistic SPX Backtest Data Generator (3 Years)")
    print("=" * 70)
    print()
    
    # 1. DB 삭제 (스킵 - FastAPI가 사용 중일 수 있음)
    print("[1/3] Database check...")
    print("[INFO] Skipping database deletion (server may be running)")
    print("[INFO] New signals will be added to existing data")
    
    # 2. 신호 생성
    print("\n[2/3] Generating realistic signals...")
    signals = generate_realistic_signals()
    print(f"[OK] Generated {len(signals)} signals")
    
    # 미리보기
    print("\nFirst 3 signals:")
    for i, sig in enumerate(signals[:3], 1):
        print(f"  {i}. {sig['action']} @ ${sig['price']:.2f} on {datetime.fromtimestamp(sig['ts_unix']).strftime('%Y-%m-%d')}")
    
    # 3. 전송
    print(f"\n[3/3] Sending signals to FastAPI...")
    print("[INFO] Please wait...")
    
    success_count = 0
    fail_count = 0
    
    for i, signal in enumerate(signals, 1):
        success, result = send_signal_to_api(signal)
        
        if success:
            success_count += 1
            if i % 10 == 0 or i == 1:
                print(f"[OK] [{i}/{len(signals)}] {signal['action']} @ ${signal['price']:.2f} -> Saved")
        else:
            fail_count += 1
            print(f"[ERROR] [{i}/{len(signals)}] Failed: {result}")
        
        time.sleep(0.05)
    
    # 결과
    print()
    print("=" * 70)
    print("[COMPLETE] GENERATION COMPLETE!")
    print("=" * 70)
    print(f"Total Signals:   {len(signals)}")
    print(f"[OK] Success:    {success_count} ({success_count/len(signals)*100:.1f}%)")
    print(f"[ERROR] Failed:  {fail_count} ({fail_count/len(signals)*100:.1f}%)")
    print()
    print(f"Date Range:      {datetime.fromtimestamp(signals[0]['ts_unix']).strftime('%Y-%m-%d')} -> {datetime.fromtimestamp(signals[-1]['ts_unix']).strftime('%Y-%m-%d')}")
    print(f"Symbol:          SPX")
    print(f"Timeframe:       1D")
    print()
    print("=" * 70)
    print("[OK] Next Steps:")
    print("   1. Open dashboard: http://localhost:8501")
    print("   2. Check 'Signal Monitoring' tab")
    print("   3. Select a signal to view analyst report")
    print("=" * 70)

if __name__ == "__main__":
    main()

