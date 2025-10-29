"""
TradingView 백테스트 결과를 FastAPI로 전송하는 스크립트

사용법:
1. TradingView Strategy Tester → "List of Trades" → CSV 다운로드
2. CSV 파일을 이 스크립트와 같은 폴더에 저장
3. python import_backtest_signals.py --csv trades.csv --symbol SPX --timeframe 1D
"""

import requests
import csv
import sys
import argparse
from datetime import datetime
import time

# FastAPI 서버 URL
API_URL = "http://localhost:8000/alert"

def parse_tradingview_csv(csv_file, symbol, timeframe):
    """
    TradingView CSV를 파싱하여 신호 목록 생성
    
    예상 CSV 형식:
    Trade #, Type, Date/Time, Entry Price, Exit Price, Profit, Duration
    1, Long, 2023-01-15 09:30, 4850.50, 4950.25, +2.05%, 3d 2h
    """
    signals = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # CSV 헤더가 다를 수 있으므로 유연하게 처리
                trade_type = row.get('Type', row.get('Signal', 'Long')).strip()
                entry_date = row.get('Date/Time', row.get('Entry Time', '')).strip()
                entry_price = float(row.get('Entry Price', row.get('Price', 0)))
                
                # 날짜 파싱
                try:
                    dt = datetime.strptime(entry_date, '%Y-%m-%d %H:%M')
                except:
                    try:
                        dt = datetime.strptime(entry_date, '%m/%d/%Y %H:%M')
                    except:
                        print(f"Warning: Could not parse date '{entry_date}', skipping...")
                        continue
                
                # 신호 타입
                action = "BUY" if "Long" in trade_type or "Buy" in trade_type else "SELL"
                
                # 신호 생성 (간소화된 v3 형식)
                signal = {
                    "ts_unix": int(dt.timestamp()),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "action": action,
                    "price": entry_price,
                    "trend_score": 65.0,  # 백테스트에서는 실제 값 알 수 없음
                    "rsi": 60.0 if action == "BUY" else 40.0,
                    "vol_mult": 1.5,
                    "ema1": entry_price * 0.99 if action == "BUY" else entry_price * 1.01,
                    "ema2": entry_price * 0.98 if action == "BUY" else entry_price * 1.02,
                    "sl_price": entry_price * 0.95 if action == "BUY" else 0,
                    "tp_price": entry_price * 1.10 if action == "BUY" else 0,
                    "version": "vmsi_sdm_v3_clean"
                }
                
                signals.append(signal)
                
            except Exception as e:
                print(f"Warning: Error parsing row: {e}")
                continue
    
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

def main():
    parser = argparse.ArgumentParser(description='Import TradingView backtest signals to FastAPI')
    parser.add_argument('--csv', required=True, help='CSV file from TradingView')
    parser.add_argument('--symbol', required=True, help='Symbol (e.g. SPX, AAPL)')
    parser.add_argument('--timeframe', required=True, help='Timeframe (e.g. 1D, 4H, 1H)')
    parser.add_argument('--clear', action='store_true', help='Clear existing signals first')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("TradingView Backtest → FastAPI Signal Importer")
    print("=" * 60)
    print(f"CSV File: {args.csv}")
    print(f"Symbol: {args.symbol}")
    print(f"Timeframe: {args.timeframe}")
    print()
    
    # 1. CSV 파싱
    print("[1/3] Parsing CSV...")
    try:
        signals = parse_tradingview_csv(args.csv, args.symbol, args.timeframe)
        print(f"✓ Found {len(signals)} signals")
    except Exception as e:
        print(f"✗ Error parsing CSV: {e}")
        return
    
    # 2. 기존 신호 삭제 (선택)
    if args.clear:
        print("\n[2/3] Clearing existing signals...")
        # TODO: DB 초기화 API 엔드포인트 필요
        print("⚠ Clear function not implemented yet")
    
    # 3. 신호 전송
    print(f"\n[{'3' if not args.clear else '2'}/3] Sending signals to FastAPI...")
    success_count = 0
    fail_count = 0
    
    for i, signal in enumerate(signals, 1):
        success, result = send_signal_to_api(signal)
        
        if success:
            success_count += 1
            print(f"✓ [{i}/{len(signals)}] {signal['action']} @ {signal['price']:.2f} → Saved")
        else:
            fail_count += 1
            print(f"✗ [{i}/{len(signals)}] Failed: {result}")
        
        # API 부하 방지
        time.sleep(0.1)
    
    # 결과 요약
    print()
    print("=" * 60)
    print("Import Complete!")
    print("=" * 60)
    print(f"Total Signals: {len(signals)}")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print()
    print("✓ Check your dashboard: http://localhost:8501")
    print("=" * 60)

if __name__ == "__main__":
    main()

