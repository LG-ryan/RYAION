#!/usr/bin/env python3
"""
yfinance를 사용한 자동 시장 데이터 수집 및 신호 생성

Features:
- 실시간 SPX, NASDAQ, Dow Jones 데이터 수집
- 자동 신호 생성 (v5 로직 적용)
- FastAPI 서버로 자동 전송
- 백테스트 데이터 생성

Usage:
    python tools/auto_collect_data.py --symbols SPX QQQ DIA --period 2y --interval 1wk
"""

import sys
import os
import argparse
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def download_market_data(symbol: str, period: str = "2y", interval: str = "1wk") -> pd.DataFrame:
    """
    yfinance를 사용하여 시장 데이터 다운로드
    
    Args:
        symbol: 티커 심볼 (^GSPC for SPX, ^IXIC for NASDAQ, ^DJI for Dow)
        period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: 간격 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    """
    print(f"[1/5] Downloading {symbol} data (period={period}, interval={interval})...")
    
    # Map common symbols to Yahoo Finance tickers
    symbol_map = {
        'SPX': '^GSPC',
        'SP500': '^GSPC',
        'NASDAQ': '^IXIC',
        'QQQ': 'QQQ',
        'DIA': 'DIA',
        'DOW': '^DJI',
        'DJIA': '^DJI'
    }
    
    ticker = symbol_map.get(symbol, symbol)
    
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if data.empty:
            raise ValueError(f"No data downloaded for {ticker}")
        
        # Rename columns to match our format
        data = data.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Reset index to get timestamp as column
        data = data.reset_index()
        data = data.rename(columns={'Date': 'time'})
        
        # Convert timestamp to Unix time
        data['time'] = data['time'].astype(int) // 10**9
        
        print(f"[OK] Downloaded {len(data)} bars")
        print(f"[INFO] Date range: {datetime.fromtimestamp(data['time'].iloc[0])} to {datetime.fromtimestamp(data['time'].iloc[-1])}")
        
        return data
    
    except Exception as e:
        print(f"[ERROR] Failed to download {ticker}: {e}")
        return None

def calculate_indicators(df: pd.DataFrame, ema1_len: int = 20, ema2_len: int = 50) -> pd.DataFrame:
    """기술적 지표 계산"""
    print("[2/5] Calculating indicators...")
    
    # EMA
    df['ema1'] = df['close'].ewm(span=ema1_len, adjust=False).mean()
    df['ema2'] = df['close'].ewm(span=ema2_len, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Volume multiplier
    df['vol_avg'] = df['volume'].rolling(20).mean()
    df['vol_mult'] = df['volume'] / df['vol_avg']
    
    # ATR
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['true_range'].rolling(14).mean()
    
    # VCP
    df['vcp_high'] = df['high'].rolling(20).max()
    df['vcp_low'] = df['low'].rolling(20).min()
    df['vcp_ratio'] = (df['vcp_high'] - df['vcp_low']) / df['vcp_high']
    
    # Trend Score (v5 weights)
    def calc_trend_score(row):
        if pd.isna(row['rsi']) or pd.isna(row['vol_mult']):
            return 50
        
        ema_above = 1.0 if row['ema1'] > row['ema2'] else 0.0
        rsi_norm = row['rsi'] / 100.0
        vol_norm = min(row['vol_mult'] / 3.0, 1.0)
        vcp_norm = 1.0 - row['vcp_ratio']
        
        alpha, beta, gamma, delta = 0.8, 0.35, 0.7, 0.6
        raw = (alpha * ema_above + beta * rsi_norm + gamma * vol_norm + delta * vcp_norm) * 100.0
        return max(0, min(100, raw))
    
    df['trend_score'] = df.apply(calc_trend_score, axis=1)
    
    print("[OK] Indicators calculated")
    return df

def generate_signals(df: pd.DataFrame, symbol: str, timeframe: str) -> list:
    """신호 생성 (v5 Final logic)"""
    print("[3/5] Generating signals...")
    
    signals = []
    buy_count = 0
    sell_count = 0
    
    for i in range(20, len(df)):  # Warmup period
        row = df.iloc[i]
        
        if pd.isna(row['rsi']) or pd.isna(row['atr']):
            continue
        
        # Buy Signal (v5 Final conditions)
        buy_condition = (
            row['ema1'] > row['ema2'] and 
            row['rsi'] > 45 and 
            row['vol_mult'] > 1.0 and
            row['trend_score'] >= 50
        )
        
        # Sell Signal (v5 Final conditions)
        sell_condition = (
            row['ema1'] < row['ema2'] and 
            row['rsi'] < 55 and 
            row['vol_mult'] > 1.0 and
            row['trend_score'] <= 50
        )
        
        if buy_condition:
            buy_count += 1
            sl_distance = row['atr'] * 1.5
            tp_distance = row['atr'] * 2.5
            
            signals.append({
                'ts_unix': int(row['time']),
                'symbol': symbol,
                'timeframe': timeframe,
                'action': 'BUY',
                'price': float(row['close']),
                'signal_number': buy_count,
                'trend_score': float(row['trend_score']),
                'prob': float(row['trend_score']) / 100.0,
                'rsi': float(row['rsi']),
                'vol_mult': float(row['vol_mult']),
                'vcp_ratio': float(row['vcp_ratio']),
                'dist_ath': 0.0,
                'ema1': float(row['ema1']),
                'ema2': float(row['ema2']),
                'sl_price': float(row['close'] - sl_distance),
                'tp_price': float(row['close'] + tp_distance),
                'atr': float(row['atr']),
                'bar_state': 'close',
                'fast_mode': False,
                'realtime_macro': False,
                'mode': 'yfinance',
                'version': 'vmsi_sdm_v5_yfinance'
            })
        
        elif sell_condition:
            sell_count += 1
            sl_distance = row['atr'] * 1.5
            tp_distance = row['atr'] * 2.5
            
            signals.append({
                'ts_unix': int(row['time']),
                'symbol': symbol,
                'timeframe': timeframe,
                'action': 'SELL',
                'price': float(row['close']),
                'signal_number': sell_count,
                'trend_score': float(row['trend_score']),
                'prob': float(row['trend_score']) / 100.0,
                'rsi': float(row['rsi']),
                'vol_mult': float(row['vol_mult']),
                'vcp_ratio': float(row['vcp_ratio']),
                'dist_ath': 0.0,
                'ema1': float(row['ema1']),
                'ema2': float(row['ema2']),
                'sl_price': float(row['close'] + sl_distance),
                'tp_price': float(row['close'] - tp_distance),
                'atr': float(row['atr']),
                'bar_state': 'close',
                'fast_mode': False,
                'realtime_macro': False,
                'mode': 'yfinance',
                'version': 'vmsi_sdm_v5_yfinance'
            })
    
    print(f"[OK] Generated {len(signals)} signals (Buy: {buy_count}, Sell: {sell_count})")
    return signals

def send_to_server(signals: list, server_url: str = "http://localhost:8000/alert") -> tuple:
    """신호를 FastAPI 서버로 전송"""
    print(f"[4/5] Sending {len(signals)} signals to server...")
    
    success_count = 0
    error_count = 0
    
    for signal in signals:
        try:
            response = requests.post(server_url, json=signal, timeout=5)
            if response.status_code == 200:
                success_count += 1
                if success_count % 10 == 0:
                    print(f"  ... {success_count}/{len(signals)}")
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"[WARN] Request failed: {e}")
    
    print(f"[OK] Sent: {success_count}, Errors: {error_count}")
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description='Auto collect market data via yfinance')
    parser.add_argument('--symbols', nargs='+', default=['SPX'], help='Symbols to collect (SPX, NASDAQ, QQQ, etc)')
    parser.add_argument('--period', type=str, default='2y', help='Period (1y, 2y, 5y, max)')
    parser.add_argument('--interval', type=str, default='1wk', help='Interval (1d, 1wk, 1mo)')
    parser.add_argument('--server', type=str, default='http://localhost:8000/alert', help='FastAPI server URL')
    parser.add_argument('--export-csv', action='store_true', help='Export to CSV instead of sending to server')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VMSI-SDM Auto Data Collection (yfinance)")
    print("=" * 70)
    print(f"Symbols:  {', '.join(args.symbols)}")
    print(f"Period:   {args.period}")
    print(f"Interval: {args.interval}")
    print("=" * 70)
    
    all_signals = []
    
    for symbol in args.symbols:
        print(f"\n{'─' * 70}")
        print(f"Processing: {symbol}")
        print(f"{'─' * 70}")
        
        # Download data
        df = download_market_data(symbol, args.period, args.interval)
        if df is None or df.empty:
            print(f"[ERROR] Skipping {symbol}")
            continue
        
        # Calculate indicators
        df = calculate_indicators(df)
        
        # Generate signals
        signals = generate_signals(df, symbol, args.interval)
        all_signals.extend(signals)
    
    # Send to server or export CSV
    if args.export_csv:
        print(f"\n[5/5] Exporting {len(all_signals)} signals to CSV...")
        df_export = pd.DataFrame(all_signals)
        filename = f"signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_export.to_csv(filename, index=False)
        print(f"[OK] Exported to {filename}")
    else:
        print(f"\n{'=' * 70}")
        success, errors = send_to_server(all_signals, args.server)
        print(f"[5/5] Complete! Success: {success}, Errors: {errors}")
        print("=" * 70)
    
    return 0 if errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

