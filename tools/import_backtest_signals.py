"""
TradingView 백테스트 결과를 FastAPI로 전송하는 스크립트 (v4 Dynamic)

사용법:
1. TradingView Strategy Tester → "List of Trades" → Export to CSV
2. CSV 파일 저장
3. python import_backtest_signals.py --csv trades.csv --symbol SPX --timeframe 1D --clear

주의: --clear 옵션은 기존 DB를 완전히 삭제합니다!
"""

import requests
import csv
import sys
import argparse
from datetime import datetime
import time
import os
from pathlib import Path

# FastAPI 서버 URL
API_URL = "http://localhost:8000/alert"

# DB 파일 경로
DB_PATH = Path(__file__).parent.parent / "vmsi_sdm.db"

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

def clear_database():
    """기존 DB 파일 삭제"""
    if DB_PATH.exists():
        try:
            os.remove(DB_PATH)
            print(f"✓ Deleted existing database: {DB_PATH}")
            return True
        except Exception as e:
            print(f"✗ Error deleting database: {e}")
            return False
    else:
        print("⚠ No existing database found")
        return True

def main():
    parser = argparse.ArgumentParser(description='Import TradingView backtest signals to FastAPI (v4 Dynamic)')
    parser.add_argument('--csv', required=True, help='CSV file from TradingView Strategy Tester')
    parser.add_argument('--symbol', required=True, help='Symbol (e.g. SPX, AAPL)')
    parser.add_argument('--timeframe', required=True, help='Timeframe (e.g. 1D, 4H, 1H)')
    parser.add_argument('--clear', action='store_true', help='⚠️  Clear existing database (DELETE ALL DATA!)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("TradingView Backtest → FastAPI Signal Importer (v4 Dynamic)")
    print("=" * 70)
    print(f"CSV File:    {args.csv}")
    print(f"Symbol:      {args.symbol}")
    print(f"Timeframe:   {args.timeframe}")
    print(f"Clear DB:    {'YES ⚠️  (ALL DATA WILL BE DELETED!)' if args.clear else 'NO'}")
    print()
    
    # 확인 프롬프트
    if args.clear:
        confirm = input("⚠️  Are you sure you want to DELETE ALL existing data? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Aborted by user")
            return
    
    # 1. 기존 신호 삭제
    if args.clear:
        print("\n[1/4] Clearing existing database...")
        if not clear_database():
            print("❌ Failed to clear database. Aborting.")
            return
        print("✓ Database cleared successfully")
        time.sleep(2)  # FastAPI가 새 DB 생성하도록 대기
    
    # 2. CSV 파싱
    step = 2 if args.clear else 1
    total_steps = 4 if args.clear else 3
    print(f"\n[{step}/{total_steps}] Parsing CSV...")
    try:
        signals = parse_tradingview_csv(args.csv, args.symbol, args.timeframe)
        print(f"✓ Found {len(signals)} signals")
        
        if len(signals) == 0:
            print("❌ No signals found in CSV. Check your file format.")
            return
        
        # 신호 미리보기
        print("\nFirst 3 signals:")
        for i, sig in enumerate(signals[:3], 1):
            print(f"  {i}. {sig['action']} @ ${sig['price']:.2f} on {datetime.fromtimestamp(sig['ts_unix']).strftime('%Y-%m-%d')}")
        
    except Exception as e:
        print(f"✗ Error parsing CSV: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 신호 전송
    step += 1
    print(f"\n[{step}/{total_steps}] Sending signals to FastAPI...")
    print("⏳ This may take a few minutes for large datasets...")
    
    success_count = 0
    fail_count = 0
    
    for i, signal in enumerate(signals, 1):
        success, result = send_signal_to_api(signal)
        
        if success:
            success_count += 1
            if i % 10 == 0 or i == 1:  # 10개마다 출력
                print(f"✓ [{i}/{len(signals)}] {signal['action']} @ ${signal['price']:.2f} → Saved")
        else:
            fail_count += 1
            print(f"✗ [{i}/{len(signals)}] Failed: {result}")
        
        # API 부하 방지
        time.sleep(0.05)
    
    # 4. 결과 요약
    step += 1
    print(f"\n[{step}/{total_steps}] Import Complete!")
    print()
    print("=" * 70)
    print("📊 IMPORT SUMMARY")
    print("=" * 70)
    print(f"Total Signals:   {len(signals)}")
    print(f"✅ Success:      {success_count} ({success_count/len(signals)*100:.1f}%)")
    print(f"❌ Failed:       {fail_count} ({fail_count/len(signals)*100:.1f}%)")
    print()
    print(f"📅 Date Range:   {datetime.fromtimestamp(signals[0]['ts_unix']).strftime('%Y-%m-%d')} → {datetime.fromtimestamp(signals[-1]['ts_unix']).strftime('%Y-%m-%d')}")
    print(f"🔢 Symbol:       {args.symbol}")
    print(f"⏱️  Timeframe:   {args.timeframe}")
    print()
    print("=" * 70)
    print("✅ Next Steps:")
    print("   1. Open dashboard: http://localhost:8501")
    print("   2. Check 'Signal Monitoring' tab")
    print("   3. Select a signal to view analyst report")
    print("=" * 70)

if __name__ == "__main__":
    main()

