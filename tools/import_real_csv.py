#!/usr/bin/env python3
"""
실제 TradingView CSV 데이터를 파싱하여 VMSI-SDM 시스템에 임포트

Usage:
    python tools/import_real_csv.py --csv "SP_SPX, 1W.csv" --symbol SPX --timeframe 1W
"""

import sys
import os
import argparse
import pandas as pd
from datetime import datetime
import requests

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_spx_csv(csv_path: str) -> list:
    """
    SPX CSV 파일을 파싱하여 BUY/SELL 신호 생성
    
    Strategy:
    - Buy: EMA1 > EMA2 + Volume spike + Price pullback recovery
    - Sell: EMA1 < EMA2 + Volume spike + Price breakdown
    """
    print(f"[1/4] Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"[OK] Loaded {len(df)} rows")
    print(f"[INFO] Date range: {df['time'].iloc[0]} to {df['time'].iloc[-1]}")
    
    signals = []
    
    # Calculate indicators
    df['ema_cross'] = (df['EMA1'] > df['EMA2']).astype(int)
    df['ema_cross_prev'] = df['ema_cross'].shift(1)
    df['vol_avg'] = df['Volume'].rolling(20).mean()
    df['vol_mult'] = df['Volume'] / df['vol_avg']
    df['price_change'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1) * 100
    
    # RSI calculation
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # ATR calculation
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['true_range'].rolling(14).mean()
    
    # VCP (Volatility Contraction Pattern)
    df['vcp_high'] = df['high'].rolling(20).max()
    df['vcp_low'] = df['low'].rolling(20).min()
    df['vcp_ratio'] = (df['vcp_high'] - df['vcp_low']) / df['vcp_high']
    
    # Trend Score calculation
    def calc_trend_score(row):
        if pd.isna(row['rsi']) or pd.isna(row['vol_mult']):
            return 50
        
        ema_above = 1.0 if row['EMA1'] > row['EMA2'] else 0.0
        rsi_norm = row['rsi'] / 100.0
        vol_norm = min(row['vol_mult'] / 3.0, 1.0)
        vcp_norm = 1.0 - row['vcp_ratio']
        
        # Weights from v5
        alpha, beta, gamma, delta = 0.8, 0.35, 0.7, 0.6
        raw = (alpha * ema_above + beta * rsi_norm + gamma * vol_norm + delta * vcp_norm) * 100.0
        return max(0, min(100, raw))
    
    df['trend_score'] = df.apply(calc_trend_score, axis=1)
    
    print("[2/4] Generating signals...")
    
    buy_count = 0
    sell_count = 0
    
    for i in range(20, len(df)):  # Start after indicator warmup
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # Skip if not enough data
        if pd.isna(row['rsi']) or pd.isna(row['atr']):
            continue
        
        # Buy Signal: EMA cross up + RSI oversold recovery + Volume
        buy_condition = (
            row['EMA1'] > row['EMA2'] and 
            row['rsi'] > 45 and row['rsi'] < 65 and
            row['vol_mult'] > 1.0 and
            row['trend_score'] >= 50
        )
        
        # Sell Signal: EMA cross down + RSI overbought + Volume
        sell_condition = (
            row['EMA1'] < row['EMA2'] and 
            row['rsi'] > 35 and row['rsi'] < 55 and
            row['vol_mult'] > 1.0 and
            row['trend_score'] <= 50
        )
        
        # Create signal
        if buy_condition:
            buy_count += 1
            sl_price = row['close'] - (row['atr'] * 1.5)
            tp_price = row['close'] + (row['atr'] * 2.5)
            
            signals.append({
                'ts_unix': int(row['time']),
                'symbol': 'SPX',
                'timeframe': '1W',
                'action': 'BUY',
                'price': float(row['close']),
                'signal_number': buy_count,
                'trend_score': float(row['trend_score']),
                'prob': float(row['trend_score']) / 100.0,  # Convert to 0-1 range
                'rsi': float(row['rsi']),
                'vol_mult': float(row['vol_mult']),
                'vcp_ratio': float(row['vcp_ratio']),
                'dist_ath': 0.0,  # Placeholder (not critical for v5)
                'ema1': float(row['EMA1']),
                'ema2': float(row['EMA2']),
                'sl_price': float(sl_price),
                'tp_price': float(tp_price),
                'atr': float(row['atr']),
                'bar_state': 'close',
                'fast_mode': False,
                'realtime_macro': False,
                'mode': 'real_data',
                'version': 'vmsi_sdm_v5_real'
            })
        
        elif sell_condition:
            sell_count += 1
            sl_price = row['close'] + (row['atr'] * 1.5)
            tp_price = row['close'] - (row['atr'] * 2.5)
            
            signals.append({
                'ts_unix': int(row['time']),
                'symbol': 'SPX',
                'timeframe': '1W',
                'action': 'SELL',
                'price': float(row['close']),
                'signal_number': sell_count,
                'trend_score': float(row['trend_score']),
                'prob': float(row['trend_score']) / 100.0,  # Convert to 0-1 range
                'rsi': float(row['rsi']),
                'vol_mult': float(row['vol_mult']),
                'vcp_ratio': float(row['vcp_ratio']),
                'dist_ath': 0.0,  # Placeholder (not critical for v5)
                'ema1': float(row['EMA1']),
                'ema2': float(row['EMA2']),
                'sl_price': float(sl_price),
                'tp_price': float(tp_price),
                'atr': float(row['atr']),
                'bar_state': 'close',
                'fast_mode': False,
                'realtime_macro': False,
                'mode': 'real_data',
                'version': 'vmsi_sdm_v5_real'
            })
    
    print(f"[OK] Generated {len(signals)} signals (Buy: {buy_count}, Sell: {sell_count})")
    return signals

def send_to_server(signals: list, server_url: str = "http://localhost:8000/alert"):
    """신호를 FastAPI 서버로 전송"""
    print(f"[3/4] Sending {len(signals)} signals to server...")
    
    success_count = 0
    error_count = 0
    
    for i, signal in enumerate(signals):
        try:
            response = requests.post(server_url, json=signal, timeout=5)
            if response.status_code == 200:
                success_count += 1
                if success_count == 1:
                    print(f"[OK] First signal sent successfully")
            else:
                error_count += 1
                if error_count <= 3:  # Only print first 3 errors
                    print(f"[ERROR] Signal failed: {signal['action']} @ {signal['ts_unix']}")
                    print(f"        HTTP {response.status_code}: {response.text}")
        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"[ERROR] Request failed: {e}")
    
    print(f"[OK] Sent: {success_count}, Errors: {error_count}")
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description='Import real CSV data to VMSI-SDM')
    parser.add_argument('--csv', type=str, required=True, help='Path to CSV file')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol name')
    parser.add_argument('--timeframe', type=str, default='1W', help='Timeframe (1W, 1D, etc)')
    parser.add_argument('--server', type=str, default='http://localhost:8000/alert', help='FastAPI server URL')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("VMSI-SDM Real Data Import Tool")
    print("=" * 60)
    
    # Check if CSV exists
    if not os.path.exists(args.csv):
        print(f"[ERROR] CSV file not found: {args.csv}")
        return 1
    
    # Parse CSV
    signals = parse_spx_csv(args.csv)
    
    if not signals:
        print("[ERROR] No signals generated")
        return 1
    
    # Send to server
    success, errors = send_to_server(signals, args.server)
    
    print("=" * 60)
    print(f"[4/4] Import complete!")
    print(f"      Success: {success}, Errors: {errors}")
    print("=" * 60)
    
    return 0 if errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

