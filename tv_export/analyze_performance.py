# -*- coding: utf-8 -*-
"""
RYAION v19.1 Universal Indicator - Deep Performance Analyzer
============================================================
Comprehensive analysis of all v19.1 indicator components for real-world performance evaluation

Analysis Modules:
1. 4-Axis Score Decomposition (Trend/Momentum/Volatility/Context)
2. Component Performance (FTD/TD/WVF)
3. VIX Regime Effect Verification
4. Stage Timing Analysis
5. Asset-Adaptive Verification
6. False Signal Patterns
7. Optimal Pattern Discovery (ML)
8. Synergy Effect Verification
9. Threshold Optimization
10. Category Performance
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 설정
# ============================================================================

EXPORTS_DIR = Path("exports")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# 백테스트 파라미터
HOLDING_PERIODS = [5, 10, 20, 40, 60]
STOP_LOSS = -0.10
TAKE_PROFIT_LEVELS = [0.10, 0.20, 0.30, 0.50]

# v19.1 파라미터
EXTREME_BASE = 18.0
STRONG_BASE = 14.0
MODERATE_BASE = 11.0

# ============================================================================
# 티커 분류 시스템
# ============================================================================

def categorize_ticker(ticker):
    """티커를 자산군별로 분류"""
    ticker_upper = ticker.upper().replace(':', '_')
    
    # 7. 암호화폐
    if any(x in ticker_upper for x in ['BTC', 'ETH', 'XRP', 'ADA', 'SOL', 'DOGE', '-USD', 'USDT', 'USDC']):
        sub = 'Major Crypto' if any(x in ticker_upper for x in ['BTC', 'ETH']) else 'Altcoins'
        return {'asset_class': 'Crypto', 'sub_category': sub}
    
    # 6. 통화
    if '/' in ticker or (len(ticker) == 6 and ticker.isupper()) or any(x in ticker_upper for x in ['EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'NZD', 'CAD']):
        return {'asset_class': 'Currency', 'sub_category': 'FX Pairs'}
    
    # 5. 상품
    if any(x in ticker_upper for x in ['GC', 'SI', 'CL', 'NG', 'HG', 'ZW', 'ZC', 'ZS', '=F']):
        if any(x in ticker_upper for x in ['GC', 'SI', 'PL', 'PA']):
            sub = '귀금속'
        elif any(x in ticker_upper for x in ['CL', 'NG', 'RB', 'HO']):
            sub = '에너지'
        elif any(x in ticker_upper for x in ['ZW', 'ZC', 'ZS', 'CC', 'SB', 'KC']):
            sub = '농산물'
        else:
            sub = '산업용 금속'
        return {'asset_class': 'Commodity', 'sub_category': sub}
    
    # 4. 채권
    if any(x in ticker_upper for x in ['TLT', 'IEF', 'SHY', 'AGG', 'BND', 'LQD', 'HYG', 'MUB', 'TIP']):
        if any(x in ticker_upper for x in ['TLT', 'IEF', 'SHY']):
            sub = '국채 ETF'
        elif any(x in ticker_upper for x in ['LQD', 'HYG']):
            sub = '회사채 ETF'
        else:
            sub = '채권 ETF'
        return {'asset_class': 'Fixed Income', 'sub_category': sub}
    
    # 3. 지수
    if ticker_upper.startswith('^') or 'VIX' in ticker_upper or ticker_upper in ['SPX', 'NDX', 'DJI', 'RUT']:
        return {'asset_class': 'Index', 'sub_category': 'Market Index'}
    
    # 2. ETF 판별
    etf_patterns = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'IVV', 'EFA', 'EEM', 'VEA', 'VWO', 
                    'XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLP', 'XLU', 'XLB', 'XLRE', 'XLC',
                    'VGT', 'VDE', 'VFH', 'VHT', 'VAW', 'VIS', 'VCR', 'VDC', 'VPU',
                    'GLD', 'SLV', 'USO', 'UNG', 'DBA',
                    'TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'SOXL', 'SOXS', 'TNA', 'TZA',
                    'ARK', 'ARKK', 'ARKG', 'ICLN', 'CLOU', 'HACK', 'BOTZ']
    
    if any(ticker_upper.startswith(x) or ticker_upper == x for x in etf_patterns):
        # ETF 세분류
        if ticker_upper in ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'IVV']:
            sub = '주식형 ETF'
        elif ticker_upper.startswith('XL') or ticker_upper.startswith('V') and len(ticker_upper) == 3:
            sub = '섹터 ETF'
        elif any(x in ticker_upper for x in ['TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'SOXL', 'SOXS', 'TNA', 'TZA']):
            sub = '레버리지/인버스 ETF'
        elif any(x in ticker_upper for x in ['GLD', 'SLV', 'USO', 'UNG', 'DBA']):
            sub = '상품형 ETF'
        elif any(x in ticker_upper for x in ['EFA', 'EEM', 'VEA', 'VWO']):
            sub = '해외 ETF'
        elif any(x in ticker_upper for x in ['ARK', 'ICLN', 'CLOU', 'HACK', 'BOTZ']):
            sub = '테마 ETF'
        else:
            sub = '주식형 ETF'
        return {'asset_class': 'ETF', 'sub_category': sub}
    
    # 1. 주식 (나머지는 모두 주식으로 가정)
    # 실전에서는 API로 시가총액 조회하여 분류
    # 여기서는 단순화: 알려진 대형주만 분류
    large_caps = ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 
                  'BRK.B', 'BRK_B', 'V', 'JNJ', 'WMT', 'JPM', 'MA', 'PG', 'UNH', 
                  'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO', 'PFE', 'TMO',
                  'ABBV', 'KO', 'PEP', 'MRK', 'COST', 'AVGO', 'NKE', 'ABT', 'DHR']
    
    if any(ticker_upper == x or ticker_upper.replace('_', '.') == x for x in large_caps):
        return {'asset_class': 'Equity', 'sub_category': '대형주'}
    else:
        # 기본값: 중소형주로 분류 (실전에서는 API 사용)
        return {'asset_class': 'Equity', 'sub_category': '중소형주'}

# ============================================================================
# 유틸리티
# ============================================================================

def safe_divide(a, b, default=0):
    """안전한 나눗셈"""
    return a / b if b != 0 else default

def calculate_metrics(results_df):
    """공통 메트릭 계산"""
    if len(results_df) == 0:
        return None
    
    win_rate = (results_df['pnl'] > 0).sum() / len(results_df)
    avg_pnl = results_df['pnl'].mean()
    median_pnl = results_df['pnl'].median()
    std_pnl = results_df['pnl'].std()
    
    sharpe = avg_pnl / std_pnl if std_pnl > 0 else 0
    
    cumulative = (1 + results_df['pnl']).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = drawdown.min()
    
    return {
        'count': len(results_df),
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'median_pnl': median_pnl,
        'std_pnl': std_pnl,
        'sharpe': sharpe,
        'max_dd': max_dd,
        'best': results_df['pnl'].max(),
        'worst': results_df['pnl'].min(),
    }

# ============================================================================
# 데이터 로드
# ============================================================================

def load_all_csvs():
    """모든 CSV 파일 로드 및 카테고리 분류"""
    csv_files = list(EXPORTS_DIR.glob("*_1D.csv"))
    
    if not csv_files:
        print("[ERROR] No CSV files found!")
        return [], {}
    
    print(f"\n[INFO] Loading {len(csv_files)} ticker data files...")
    print("="*80)
    
    data_list = []
    ticker_categories = {}
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            ticker = csv_file.stem.replace("_1D", "").replace("_", ":")
            df['ticker'] = ticker
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            
            # 티커 분류
            category = categorize_ticker(ticker)
            df['asset_class'] = category['asset_class']
            df['sub_category'] = category['sub_category']
            ticker_categories[ticker] = category
            
            data_list.append(df)
            print(f"  [OK] {ticker}: {len(df)} rows | {category['asset_class']} > {category['sub_category']}")
            
        except Exception as e:
            print(f"  [WARN] {csv_file.name} failed: {e}")
    
    return data_list, ticker_categories

# ============================================================================
# 백테스트 엔진
# ============================================================================

def backtest_signals(df, signal_col, holding=20, is_sell=False):
    """신호 백테스트 (매수/매도)"""
    signals = df[df[signal_col] == 1].copy()
    
    if len(signals) == 0:
        return pd.DataFrame()
    
    results = []
    
    for idx, row in signals.iterrows():
        entry_price = row['close']
        entry_idx = df.index.get_loc(idx)
        exit_idx = entry_idx + holding
        
        if exit_idx >= len(df):
            continue
        
        exit_price = df.iloc[exit_idx]['close']
        holding_slice = df.iloc[entry_idx:exit_idx+1]
        
        max_price = holding_slice['high'].max()
        min_price = holding_slice['low'].min()
        
        # 매도 신호는 PnL 반대 (가격 하락 시 수익)
        if is_sell:
            pnl = (entry_price - exit_price) / entry_price  # 반대
            max_gain = (entry_price - min_price) / entry_price  # 하락이 이익
            max_loss = (max_price - entry_price) / entry_price  # 상승이 손실
        else:
            pnl = (exit_price - entry_price) / entry_price
            max_gain = (max_price - entry_price) / entry_price
            max_loss = (min_price - entry_price) / entry_price
        
        hit_sl = max_loss <= STOP_LOSS
        hit_tp = max_gain >= 0.20
        
        results.append({
            'ticker': row['ticker'],
            'entry_date': row['datetime'],
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl': pnl,
            'max_gain': max_gain,
            'max_loss': max_loss,
            'hit_sl': hit_sl,
            'hit_tp': hit_tp,
            'bottom_score': row.get('Bottom Score', 0),
            'top_score': row.get('Top Score', 0),
            'stage': row.get('Stage', 0),
            'vix_regime': row.get('VIX Regime (0=LOW/1=NORMAL/2=HIGH)', 1),
            'trend_score': row.get('Trend Score', 0),
            'momentum_score': row.get('Momentum Score', 0),
            'volatility_score': row.get('Volatility Score', 0),
            'context_score': row.get('Context Score', 0),
            'ftd_confirmed': row.get('FTD Confirmed', 0),
            'ftd_candidate': row.get('FTD Candidate', 0),
            'td_buy_count': row.get('TD Buy Count', 0),
            'td_buy_9': row.get('TD Buy 9', 0),
            'td_buy_13': row.get('TD Buy 13+', 0),
            'wvf_extreme': row.get('WVF Extreme', 0),
            'wvf_filtered': row.get('WVF Filtered', 0),
            'rsi': row.get('RSI', 50),
            'vix': row.get('VIX', 20),
        })
    
    return pd.DataFrame(results)

# ============================================================================
# 0. 대분류별 요약 분석
# ============================================================================

def analyze_by_asset_class(df_list, ticker_categories):
    """대분류(자산군)별 요약 분석"""
    print("\n[INFO] Analyzing by asset class...")
    print("="*80)
    
    all_data = pd.concat(df_list, ignore_index=True)
    
    # 자산군별 그룹화
    asset_summary = {}
    
    for asset_class in ['Equity', 'ETF', 'Index', 'Fixed Income', 'Commodity', 'Currency', 'Crypto']:
        class_data = all_data[all_data['asset_class'] == asset_class]
        
        if len(class_data) == 0:
            continue
        
        # 기본 통계
        tickers = class_data['ticker'].unique()
        total_bars = len(class_data)
        extreme_buy = int(class_data['Buy Extreme Signal'].sum()) if 'Buy Extreme Signal' in class_data.columns else 0
        strong_buy = int(class_data['Buy Strong Signal'].sum()) if 'Buy Strong Signal' in class_data.columns else 0
        
        # 간단한 백테스트 (EXTREME, 20일)
        if 'Buy Extreme Signal' in class_data.columns:
            extreme_signals = class_data[class_data['Buy Extreme Signal'] == 1]
        else:
            extreme_signals = pd.DataFrame()
        
        if len(extreme_signals) > 0:
            # 승률 계산
            win_count = 0
            total_trades = 0
            pnl_list = []
            
            for idx, row in extreme_signals.iterrows():
                ticker = row['ticker']
                ticker_df = all_data[all_data['ticker'] == ticker].reset_index(drop=True)
                
                signal_idx = ticker_df[ticker_df['time'] == row['time']].index
                if len(signal_idx) == 0:
                    continue
                signal_idx = signal_idx[0]
                
                exit_idx = signal_idx + 20
                if exit_idx >= len(ticker_df):
                    continue
                
                entry_price = ticker_df.iloc[signal_idx]['close']
                exit_price = ticker_df.iloc[exit_idx]['close']
                pnl = (exit_price - entry_price) / entry_price
                
                pnl_list.append(pnl)
                total_trades += 1
                if pnl > 0:
                    win_count += 1
            
            win_rate = win_count / total_trades if total_trades > 0 else 0
            avg_pnl = np.mean(pnl_list) if pnl_list else 0
        else:
            win_rate = 0
            avg_pnl = 0
            total_trades = 0
        
        asset_summary[asset_class] = {
            'tickers': list(tickers),
            'ticker_count': len(tickers),
            'total_bars': total_bars,
            'extreme_buy_count': extreme_buy,
            'extreme_buy_rate': extreme_buy / total_bars if total_bars > 0 else 0,
            'strong_buy_count': strong_buy,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'total_trades': total_trades,
        }
        
        print(f"  {asset_class:15} | {len(tickers):2}개 티커 | EXTREME {extreme_buy:3}개 | 승률 {win_rate*100:5.1f}%")
    
    return asset_summary

# ============================================================================
# 1. 신호 통계
# ============================================================================

def analyze_signals(df_list):
    """전체 신호 통계"""
    all_data = pd.concat(df_list, ignore_index=True)
    
    # 매도 신호 컬럼 확인 (두 가지 형식 지원)
    has_sell_signal = 'Sell Extreme Signal' in all_data.columns
    has_sell_raw = 'EXTREME SELL' in all_data.columns
    
    result = {
        'total_bars': len(all_data),
        'extreme_buy': int(all_data['Buy Extreme Signal'].sum()),
        'strong_buy': int(all_data['Buy Strong Signal'].sum()),
        'moderate_buy': int(all_data['Buy Moderate Signal'].sum()),
        'risk_high': int(all_data['Risk High Signal'].sum()),
        'ftd_confirmed': int(all_data['FTD Confirmed'].sum()),
        'ftd_candidate': int(all_data['FTD Candidate'].sum()),
        'stage_dist': all_data['Stage'].value_counts().sort_index().to_dict(),
        'vix_regime_dist': all_data['VIX Regime (0=LOW/1=NORMAL/2=HIGH)'].value_counts().to_dict(),
    }
    
    # 매도 신호 처리 (처리된 신호 또는 원시 데이터)
    if has_sell_signal:
        result['extreme_sell'] = int(all_data['Sell Extreme Signal'].sum())
        result['strong_sell'] = int(all_data['Sell Strong Signal'].sum())
        result['moderate_sell'] = int(all_data['Sell Moderate Signal'].sum())
    elif has_sell_raw:
        result['extreme_sell'] = int(all_data['EXTREME SELL'].sum())
        result['strong_sell'] = int(all_data['STRONG SELL'].sum())
        result['moderate_sell'] = int(all_data['SELL'].sum())
    else:
        result['extreme_sell'] = 0
        result['strong_sell'] = 0
        result['moderate_sell'] = 0
    
    return result

# ============================================================================
# 2. 기본 백테스트
# ============================================================================

def run_basic_backtest(df_list):
    """기본 백테스트"""
    print("\n[INFO] Running basic backtest...")
    print("="*80)
    
    results = {}
    
    # 매도 신호 컬럼 존재 여부 확인 (두 가지 형식 지원)
    has_sell_signal = 'Sell Extreme Signal' in df_list[0].columns if df_list else False
    has_sell_raw = 'EXTREME SELL' in df_list[0].columns if df_list else False
    
    signals = [
        ('Buy Extreme Signal', 'BUY_EXTREME'),
        ('Buy Strong Signal', 'BUY_STRONG'),
        ('Buy Moderate Signal', 'BUY_MODERATE'),
    ]
    
    # 매도 신호 추가 (처리된 신호 또는 원시 데이터)
    if has_sell_signal:
        signals.extend([
            ('Sell Extreme Signal', 'SELL_EXTREME'),
            ('Sell Strong Signal', 'SELL_STRONG'),
            ('Sell Moderate Signal', 'SELL_MODERATE'),
        ])
    elif has_sell_raw:
        signals.extend([
            ('EXTREME SELL', 'SELL_EXTREME'),
            ('STRONG SELL', 'SELL_STRONG'),
            ('SELL', 'SELL_MODERATE'),
        ])
    
    for signal_col, signal_name in signals:
        results[signal_name] = {}
        
        for holding in HOLDING_PERIODS:
            all_results = []
            
            for df in df_list:
                bt_results = backtest_signals(df, signal_col, holding, is_sell='SELL' in signal_name)
                if len(bt_results) > 0:
                    all_results.append(bt_results)
            
            if all_results:
                combined = pd.concat(all_results, ignore_index=True)
                metrics = calculate_metrics(combined)
                
                if metrics:
                    metrics['holding'] = holding
                    metrics['all_trades'] = combined
                    results[signal_name][holding] = metrics
                    
                    print(f"  {signal_name:15} {holding:2}일: 신호 {metrics['count']:3}개 | 승률 {metrics['win_rate']*100:5.1f}% | 평균 {metrics['avg_pnl']*100:+6.2f}%")
    
    return results

# ============================================================================
# 3. 4축 스코어 분해 분석
# ============================================================================

def analyze_score_components(df_list, backtest_results):
    """4축 점수 분해 분석"""
    print("\n[INFO] Analyzing 4-axis score decomposition...")
    print("="*80)
    
    # BUY_EXTREME 신호의 거래만 분석
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    if len(trades) == 0:
        return {}
    
    analysis = {}
    
    # 각 축별 분석
    axes = ['trend_score', 'momentum_score', 'volatility_score', 'context_score']
    axis_names = ['Trend', 'Momentum', 'Volatility', 'Context']
    
    for axis, name in zip(axes, axis_names):
        # 점수 구간별 승률
        bins = [0, 2, 3.5, 5.1]
        labels = ['Low (0-2)', 'Mid (2-3.5)', 'High (3.5-5)']
        
        trades[f'{axis}_bin'] = pd.cut(trades[axis], bins=bins, labels=labels, include_lowest=True)
        
        axis_analysis = {}
        for bin_label in labels:
            bin_trades = trades[trades[f'{axis}_bin'] == bin_label]
            if len(bin_trades) > 0:
                metrics = calculate_metrics(bin_trades)
                axis_analysis[bin_label] = metrics
                print(f"  {name:12} {bin_label:15}: {metrics['count']:2}개 | 승률 {metrics['win_rate']*100:5.1f}%")
        
        analysis[name] = axis_analysis
    
    # 최강 조합 찾기
    print(f"\n  [BEST] Optimal combinations:")
    strong_combos = trades[
        (trades['trend_score'] >= 4) & 
        (trades['context_score'] >= 8)
    ]
    if len(strong_combos) > 0:
        metrics = calculate_metrics(strong_combos)
        print(f"     Trend 4+ & Context 8+: {metrics['count']}개 | 승률 {metrics['win_rate']*100:.1f}%")
        analysis['best_combo'] = metrics
    
    return analysis

# ============================================================================
# 4. FTD/TD/WVF 컴포넌트 분석
# ============================================================================

def analyze_components(df_list, backtest_results):
    """FTD, TD, WVF 개별 성능"""
    print("\n[INFO] Analyzing key components...")
    print("="*80)
    
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    analysis = {}
    
    # FTD
    ftd_trades = trades[trades['ftd_confirmed'] == 1]
    if len(ftd_trades) > 0:
        metrics = calculate_metrics(ftd_trades)
        analysis['FTD Confirmed'] = metrics
        print(f"  FTD Confirmed: {metrics['count']}개 | 승률 {metrics['win_rate']*100:.1f}%")
    
    # TD Sequential
    td9_trades = trades[trades['td_buy_9'] == 1]
    td13_trades = trades[trades['td_buy_13'] == 1]
    
    if len(td9_trades) > 0:
        metrics = calculate_metrics(td9_trades)
        analysis['TD Buy 9'] = metrics
        print(f"  TD Buy 9: {metrics['count']}개 | 승률 {metrics['win_rate']*100:.1f}%")
    
    if len(td13_trades) > 0:
        metrics = calculate_metrics(td13_trades)
        analysis['TD Buy 13+'] = metrics
        print(f"  TD Buy 13+: {metrics['count']}개 | 승률 {metrics['win_rate']*100:.1f}%")
    
    # WVF
    wvf_trades = trades[trades['wvf_extreme'] == 1]
    if len(wvf_trades) > 0:
        metrics = calculate_metrics(wvf_trades)
        analysis['WVF Extreme'] = metrics
        print(f"  WVF Extreme: {metrics['count']}개 | 승률 {metrics['win_rate']*100:.1f}%")
    
    return analysis

# ============================================================================
# 5. VIX 레짐 효과
# ============================================================================

def analyze_vix_regime(df_list, backtest_results):
    """VIX 레짐별 성능"""
    print("\n[INFO] Analyzing VIX regime effects...")
    print("="*80)
    
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    regime_names = {0: 'LOW', 1: 'NORMAL', 2: 'HIGH'}
    regime_adjusts = {0: +3.0, 1: 0.0, 2: -2.0}
    
    analysis = {}
    
    for regime_val, regime_name in regime_names.items():
        regime_trades = trades[trades['vix_regime'] == regime_val]
        
        if len(regime_trades) > 0:
            metrics = calculate_metrics(regime_trades)
            analysis[regime_name] = metrics
            
            adjust = regime_adjusts[regime_val]
            print(f"  VIX {regime_name:7} (조정 {adjust:+.0f}점): {metrics['count']:2}개 | 승률 {metrics['win_rate']*100:5.1f}%")
    
    return analysis

# ============================================================================
# 6. Stage 타이밍 분석
# ============================================================================

def analyze_stage_timing(df_list, backtest_results):
    """Stage별/전환 시점 성능"""
    print("\n[INFO] Analyzing stage timing...")
    print("="*80)
    
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    analysis = {}
    
    for stage in [1, 2, 3, 4]:
        stage_trades = trades[trades['stage'] == stage]
        
        if len(stage_trades) > 0:
            metrics = calculate_metrics(stage_trades)
            analysis[f'Stage {stage}'] = metrics
            print(f"  Stage {stage}: {metrics['count']:2}개 | 승률 {metrics['win_rate']*100:5.1f}%")
    
    return analysis

# ============================================================================
# 7. False Signal 분석
# ============================================================================

def analyze_false_signals(df_list, backtest_results):
    """손실 신호 패턴 분석"""
    print("\n[INFO] Analyzing false signal patterns...")
    print("="*80)
    
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    # 손실 거래만
    losses = trades[trades['pnl'] < 0]
    wins = trades[trades['pnl'] > 0]
    
    if len(losses) == 0:
        print("  [OK] No losses!")
        return {}
    
    analysis = {
        'total_losses': len(losses),
        'total_wins': len(wins),
        'patterns': []
    }
    
    # 패턴 1: WVF 빈도
    wvf_in_losses = (losses['wvf_extreme'] == 1).sum()
    wvf_in_wins = (wins['wvf_extreme'] == 1).sum()
    
    loss_wvf_rate = wvf_in_losses / len(losses) if len(losses) > 0 else 0
    win_wvf_rate = wvf_in_wins / len(wins) if len(wins) > 0 else 0
    
    if loss_wvf_rate > win_wvf_rate * 1.5:
        pattern = f"WVF Extreme: Loss {loss_wvf_rate*100:.0f}% vs Win {win_wvf_rate*100:.0f}%"
        analysis['patterns'].append(pattern)
        print(f"  [WARN] {pattern}")
    
    # 패턴 2: Volatility Score 과도
    high_vol_losses = (losses['volatility_score'] >= 4.5).sum()
    high_vol_rate = high_vol_losses / len(losses) if len(losses) > 0 else 0
    
    if high_vol_rate > 0.5:
        pattern = f"High Volatility (4.5+): {high_vol_rate*100:.0f}% of losses"
        analysis['patterns'].append(pattern)
        print(f"  [WARN] {pattern}")
    
    # 패턴 3: Stage 분포
    loss_stage_dist = losses['stage'].value_counts()
    for stage, count in loss_stage_dist.items():
        rate = count / len(losses)
        if rate > 0.4:
            pattern = f"Stage {stage}: {rate*100:.0f}% of losses ({count} signals)"
            analysis['patterns'].append(pattern)
            print(f"  [WARN] {pattern}")
    
    return analysis

# ============================================================================
# 8. 최적 조합 발견 (간이 ML)
# ============================================================================

def find_optimal_patterns(df_list, backtest_results):
    """고승률 패턴 자동 발견"""
    print("\n[INFO] Finding optimal patterns...")
    print("="*80)
    
    if 'BUY_EXTREME' not in backtest_results or 20 not in backtest_results['BUY_EXTREME']:
        return {}
    
    trades = backtest_results['BUY_EXTREME'][20]['all_trades']
    
    if len(trades) < 10:
        return {}
    
    patterns = []
    
    # 패턴 1: High Context + Stage 4/1
    pattern1 = trades[
        (trades['context_score'] >= 9) & 
        (trades['stage'].isin([1, 4]))
    ]
    if len(pattern1) >= 3:
        metrics = calculate_metrics(pattern1)
        if metrics['win_rate'] >= 0.7:
            patterns.append({
                'name': 'Context 9+ & Stage 1/4',
                'count': metrics['count'],
                'win_rate': metrics['win_rate'],
                'avg_pnl': metrics['avg_pnl'],
            })
            print(f"  패턴 1: Context 9+ & Stage 1/4 → {metrics['count']}개, 승률 {metrics['win_rate']*100:.1f}%")
    
    # 패턴 2: FTD + High VIX
    pattern2 = trades[
        (trades['ftd_confirmed'] == 1) & 
        (trades['vix'] > 25)
    ]
    if len(pattern2) >= 3:
        metrics = calculate_metrics(pattern2)
        if metrics['win_rate'] >= 0.7:
            patterns.append({
                'name': 'FTD Confirmed & VIX 25+',
                'count': metrics['count'],
                'win_rate': metrics['win_rate'],
                'avg_pnl': metrics['avg_pnl'],
            })
            print(f"  패턴 2: FTD & VIX 25+ → {metrics['count']}개, 승률 {metrics['win_rate']*100:.1f}%")
    
    # 패턴 3: High Bottom Score
    pattern3 = trades[trades['bottom_score'] >= 20]
    if len(pattern3) >= 3:
        metrics = calculate_metrics(pattern3)
        patterns.append({
            'name': 'Bottom Score 20+',
            'count': metrics['count'],
            'win_rate': metrics['win_rate'],
            'avg_pnl': metrics['avg_pnl'],
        })
        print(f"  패턴 3: Bottom 20+ → {metrics['count']}개, 승률 {metrics['win_rate']*100:.1f}%")
    
    return {'patterns': patterns}

# ============================================================================
# 9. 임계값 최적화
# ============================================================================

def optimize_thresholds(df_list):
    """최적 임계값 탐색"""
    print("\n[INFO] Optimizing thresholds...")
    print("="*80)
    
    # EXTREME 임계값 테스트: 16, 17, 18, 19, 20
    thresholds = [16, 17, 18, 19, 20, 21]
    
    results = []
    
    for threshold in thresholds:
        all_trades = []
        
        for df in df_list:
            # 임시로 임계값 적용
            temp_signals = df[df['Bottom Score'] >= threshold].copy()
            
            if len(temp_signals) == 0:
                continue
            
            # 백테스트
            signal_results = []
            for idx, row in temp_signals.iterrows():
                entry_idx = df.index.get_loc(idx)
                exit_idx = entry_idx + 20
                
                if exit_idx >= len(df):
                    continue
                
                entry_price = row['close']
                exit_price = df.iloc[exit_idx]['close']
                pnl = (exit_price - entry_price) / entry_price
                
                signal_results.append({'pnl': pnl})
            
            if signal_results:
                all_trades.extend(signal_results)
        
        if all_trades:
            trades_df = pd.DataFrame(all_trades)
            metrics = calculate_metrics(trades_df)
            
            results.append({
                'threshold': threshold,
                'count': metrics['count'],
                'win_rate': metrics['win_rate'],
                'avg_pnl': metrics['avg_pnl'],
            })
            
            marker = " ← 현재" if threshold == 18 else ""
            print(f"  임계값 {threshold:2}점: {metrics['count']:3}개 | 승률 {metrics['win_rate']*100:5.1f}% | 평균 {metrics['avg_pnl']*100:+6.2f}%{marker}")
    
    # 최적값 찾기 (승률 우선)
    if results:
        best = max(results, key=lambda x: x['win_rate'])
        print(f"\n  [BEST] Optimal: {best['threshold']} points (Win rate {best['win_rate']*100:.1f}%)")
        
        return {'results': results, 'best': best}
    
    return {}

# ============================================================================
# HTML 보고서 생성 (대폭 확장)
# ============================================================================

def generate_html_report(
    asset_summary,
    ticker_categories,
    signal_stats,
    backtest_results,
    score_analysis,
    component_analysis,
    vix_analysis,
    stage_analysis,
    false_analysis,
    optimal_patterns,
    threshold_opt,
):
    """Clean professional HTML report with asset class filter"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RYAION v19.1 심층 성능 분석 보고서</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
        }}
        .header {{
            background: #1a202c;
            color: white;
            padding: 48px 32px;
            border-bottom: 4px solid #4a5568;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}
        .header .subtitle {{
            font-size: 14px;
            color: #a0aec0;
            font-weight: 400;
        }}
        .nav {{
            background: white;
            padding: 0;
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .nav a {{
            display: inline-block;
            color: #4a5568;
            text-decoration: none;
            padding: 16px 20px;
            font-size: 13px;
            font-weight: 500;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }}
        .nav a:hover {{
            color: #2d3748;
            border-bottom-color: #4a5568;
            background: #f7fafc;
        }}
        .content {{
            padding: 32px;
        }}
        .section {{
            margin-bottom: 48px;
            padding: 32px;
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
        }}
        .section h2 {{
            color: #1a202c;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 2px solid #edf2f7;
        }}
        .section h3 {{
            color: #2d3748;
            font-size: 18px;
            font-weight: 600;
            margin: 24px 0 16px 0;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        .metric-card {{
            background: #f7fafc;
            padding: 20px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
        }}
        .metric-card .label {{
            font-size: 12px;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .metric-card .value {{
            font-size: 28px;
            font-weight: 600;
            color: #1a202c;
        }}
        .metric-card .unit {{
            font-size: 14px;
            color: #a0aec0;
            margin-left: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background: #edf2f7;
            color: #2d3748;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #cbd5e0;
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid #e2e8f0;
        }}
        tr:hover {{
            background: #f7fafc;
        }}
        .positive {{ color: #38a169; font-weight: 600; }}
        .negative {{ color: #e53e3e; font-weight: 600; }}
        .neutral {{ color: #d69e2e; font-weight: 600; }}
        .highlight-box {{
            background: #f7fafc;
            padding: 16px 20px;
            border-radius: 6px;
            border-left: 4px solid;
            margin: 16px 0;
        }}
        .box-success {{ border-color: #38a169; }}
        .box-warning {{ border-color: #d69e2e; }}
        .box-danger {{ border-color: #e53e3e; }}
        .box-info {{ border-color: #3182ce; }}
        .insight {{
            background: #edf2f7;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #4a5568;
        }}
        .insight strong {{
            font-size: 15px;
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
            color: #2d3748;
        }}
        .pattern-card {{
            background: white;
            padding: 20px;
            border-radius: 6px;
            margin: 16px 0;
            border: 1px solid #e2e8f0;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            margin-right: 8px;
        }}
        .badge-success {{ background: #c6f6d5; color: #22543d; }}
        .badge-warning {{ background: #fef3c7; color: #78350f; }}
        .badge-danger {{ background: #fed7d7; color: #742a2a; }}
        .badge-info {{ background: #bee3f8; color: #2c5282; }}
        .footer {{
            background: #1a202c;
            color: #a0aec0;
            padding: 32px;
            text-align: center;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>RYAION v19.1 유니버설 인디케이터 - 심층 성능 분석 보고서</h1>
            <div class="subtitle">생성일시: {timestamp}</div>
        </div>
        
        <div class="nav">
            <a href="#asset-dashboard">📊 자산군별 대시보드</a>
            <a href="#overview">개요</a>
            <a href="#backtest-buy">매수 백테스트</a>
            <a href="#backtest-sell">매도 백테스트</a>
            <a href="#score">4축 분해</a>
            <a href="#components">핵심 컴포넌트</a>
            <a href="#vix">VIX 레짐</a>
            <a href="#stage">Stage 분석</a>
            <a href="#false">실패 패턴</a>
            <a href="#patterns">최적 패턴</a>
            <a href="#threshold">임계값 최적화</a>
            <a href="#recommendations">최종 권장사항</a>
        </div>
        
        <div class="content">
"""
    
    # 0. Asset Class Dashboard
    html += """
            <section class="section" id="asset-dashboard">
                <h2>📊 자산군별 성과 대시보드</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>전체 데이터를 <strong>자산군별</strong>로 분류하여 요약한 대시보드입니다. 각 자산군마다 인디케이터가 얼마나 잘 작동하는지 한눈에 파악할 수 있습니다.</p>
                    <p><strong>왜 중요한가요?</strong> 주식/ETF/상품 등 자산군마다 최적 전략이 다릅니다. 이 대시보드로 어느 자산군에 집중할지 결정하세요.</p>
                    <p><strong>세분류 재분석:</strong> 특정 자산군을 더 깊이 분석하고 싶다면, 하단의 "재분석" 버튼을 클릭하세요!</p>
                </div>
"""
    
    # 자산군별 설명
    asset_descriptions = {
        'Equity': '개별 주식으로, 기업의 실적과 성장성에 따라 가격이 결정됩니다. 높은 수익률을 기대할 수 있지만 변동성도 큽니다.',
        'ETF': '여러 자산을 묶어 상장한 펀드입니다. 분산 투자가 가능하며, 섹터/지수/레버리지 등 다양한 전략이 있습니다.',
        'Index': 'S&P500, 나스닥 등 시장 전체의 움직임을 나타냅니다. 시장 타이밍 전략에 유용합니다.',
        'Fixed Income': '채권 및 채권 ETF로, 안정적인 수익을 추구합니다. 금리 변동에 민감하며, 포트폴리오 안정화에 사용됩니다.',
        'Commodity': '금, 원유, 농산물 등 실물 자산입니다. 인플레이션 헤지 및 포트폴리오 다변화에 활용됩니다.',
        'Currency': '외환 쌍(FX Pairs)으로, 글로벌 경제 흐름과 중앙은행 정책에 따라 움직입니다.',
        'Crypto': '비트코인, 이더리움 등 암호화폐입니다. 높은 변동성과 24시간 거래가 특징입니다.',
    }
    
    if asset_summary:
        html += '<div class="metric-grid">'
        
        for asset_class, stats in asset_summary.items():
            wr_class = 'positive' if stats['win_rate'] >= 0.6 else 'neutral' if stats['win_rate'] >= 0.5 else 'negative'
            tickers_text = ', '.join(stats['tickers'][:10])
            if len(stats['tickers']) > 10:
                tickers_text += f' ... (+{len(stats["tickers"]) - 10}개)'
            
            description = asset_descriptions.get(asset_class, '이 자산군에 대한 설명이 준비 중입니다.')
            
            html += f"""
                <div class="metric-card" style="cursor: pointer; position: relative;" onclick="toggleTickers('{asset_class}')">
                    <div class="label" style="font-weight: 600; font-size: 16px;">{asset_class}</div>
                    <div class="value" style="margin: 8px 0;">{stats['ticker_count']}개 티커</div>
                    <div style="font-size: 12px; color: #4a5568; line-height: 1.4; margin-bottom: 8px; min-height: 40px;">
                        {description}
                    </div>
                    <div style="font-size: 13px; color: #718096; border-top: 1px solid #e2e8f0; padding-top: 8px; margin-top: 8px;">
                        EXTREME: {stats['extreme_buy_count']}개<br>
                        승률: <span class="{wr_class}">{stats['win_rate']*100:.1f}%</span> | 
                        평균: <span class="positive">{stats['avg_pnl']*100:+.2f}%</span>
                    </div>
                    <div id="tickers-{asset_class}" style="display: none; margin-top: 10px; padding: 10px; background: #f7fafc; border-radius: 4px; font-size: 11px; color: #2d3748; max-height: 100px; overflow-y: auto;">
                        <strong>포함 티커:</strong><br>{tickers_text}
                    </div>
                    <div style="position: absolute; top: 10px; right: 10px; font-size: 18px; color: #cbd5e0;">▼</div>
                </div>
"""
        
        html += '</div>'
        
        # 세분류 데이터 준비 (JavaScript에서 사용)
        sub_categories_by_asset = {}
        for ticker, cat_info in ticker_categories.items():
            asset = cat_info['asset_class']
            sub = cat_info['sub_category']
            if asset not in sub_categories_by_asset:
                sub_categories_by_asset[asset] = set()
            sub_categories_by_asset[asset].add(sub)
        
        # Set을 list로 변환
        for asset in sub_categories_by_asset:
            sub_categories_by_asset[asset] = sorted(list(sub_categories_by_asset[asset]))
        
        import json
        sub_categories_json = json.dumps(sub_categories_by_asset, ensure_ascii=False)
        
        # 재분석 버튼
        html += f"""
                <div style="margin-top: 30px; padding: 20px; background: #edf2f7; border-radius: 6px;">
                    <h3 style="margin-bottom: 15px;">🔍 세분류 재분석</h3>
                    <p style="margin-bottom: 15px; color: #4a5568;">특정 자산군의 세부 카테고리만으로 재분석하여 최적화된 전략을 찾으세요!</p>
                    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                        <select id="asset-class-filter" onchange="updateSubCategories()" style="padding: 10px; font-size: 14px; border: 1px solid #cbd5e0; border-radius: 4px; min-width: 150px;">
                            <option value="">자산군 선택</option>
"""
        
        for asset_class in asset_summary.keys():
            html += f'                            <option value="{asset_class}">{asset_class}</option>\n'
        
        html += f"""
                        </select>
                        <select id="sub-category-filter" style="padding: 10px; font-size: 14px; border: 1px solid #cbd5e0; border-radius: 4px; min-width: 150px;">
                            <option value="">세분류 선택 (선택사항)</option>
                        </select>
                        <button onclick="runReanalysis()" style="padding: 10px 20px; background: #4a5568; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; transition: background 0.2s;">
                            재분석 실행
                        </button>
                    </div>
                    <p style="margin-top: 10px; font-size: 12px; color: #718096;">
                        ※ 재분석하면 선택한 카테고리만의 최적 임계값, 보유기간 등을 찾을 수 있습니다.<br>
                        ※ 자산군만 선택하면 해당 자산군 전체를 재분석하고, 세분류까지 선택하면 더 세밀한 분석이 가능합니다.
                    </p>
                    <div id="reanalysis-status" style="margin-top: 10px; padding: 10px; background: white; border-radius: 4px; display: none;"></div>
                </div>
                
                <script>
                    // 세분류 데이터
                    const subCategoriesData = {sub_categories_json};
                    
                    // 티커 목록 토글
                    function toggleTickers(assetClass) {{
                        const elem = document.getElementById('tickers-' + assetClass);
                        if (elem.style.display === 'none') {{
                            elem.style.display = 'block';
                        }} else {{
                            elem.style.display = 'none';
                        }}
                    }}
                    
                    // 세분류 업데이트
                    function updateSubCategories() {{
                        const assetSelect = document.getElementById('asset-class-filter');
                        const subSelect = document.getElementById('sub-category-filter');
                        const selectedAsset = assetSelect.value;
                        
                        // 세분류 초기화
                        subSelect.innerHTML = '<option value="">세분류 선택 (선택사항)</option>';
                        
                        if (selectedAsset && subCategoriesData[selectedAsset]) {{
                            subCategoriesData[selectedAsset].forEach(sub => {{
                                const option = document.createElement('option');
                                option.value = sub;
                                option.textContent = sub;
                                subSelect.appendChild(option);
                            }});
                        }}
                    }}
                    
                    // 재분석 실행
                    function runReanalysis() {{
                        const assetSelect = document.getElementById('asset-class-filter');
                        const subSelect = document.getElementById('sub-category-filter');
                        const statusDiv = document.getElementById('reanalysis-status');
                        
                        const asset = assetSelect.value;
                        const sub = subSelect.value;
                        
                        if (!asset) {{
                            alert('자산군을 먼저 선택해주세요!');
                            return;
                        }}
                        
                        // 상태 표시
                        statusDiv.style.display = 'block';
                        statusDiv.style.background = '#fff3cd';
                        statusDiv.style.color = '#856404';
                        statusDiv.innerHTML = '🔄 재분석 준비 중...<br><br>아래 명령어를 복사하여 터미널(또는 CMD)에서 실행하세요:';
                        
                        // 명령어 생성
                        let command = 'cd "C:\\\\Users\\\\ryanj\\\\RYAION\\\\tv_export" && python analyze_performance.py "' + asset + '"';
                        if (sub) {{
                            command += ' "' + sub + '"';
                        }}
                        
                        // 명령어 표시
                        statusDiv.innerHTML += '<br><div style="margin-top: 10px; padding: 10px; background: #2d3748; color: #f7fafc; border-radius: 4px; font-family: monospace; font-size: 12px; word-break: break-all; cursor: pointer;" onclick="copyCommand(this)" title="클릭하여 복사">' + command + '</div>';
                        statusDiv.innerHTML += '<p style="margin-top: 10px; font-size: 11px; color: #6c757d;">💡 명령어를 클릭하면 클립보드에 복사됩니다. 터미널에 붙여넣기(Ctrl+V)하여 실행하세요!</p>';
                    }}
                    
                    // 명령어 복사
                    function copyCommand(elem) {{
                        const text = elem.textContent;
                        navigator.clipboard.writeText(text).then(() => {{
                            const original = elem.innerHTML;
                            elem.innerHTML = '✓ 복사 완료!';
                            elem.style.background = '#48bb78';
                            setTimeout(() => {{
                                elem.innerHTML = original;
                                elem.style.background = '#2d3748';
                            }}, 1500);
                        }}).catch(err => {{
                            alert('복사 실패. 수동으로 복사해주세요.');
                        }});
                    }}
                </script>
"""
    
    html += "</section>"
    
    # 1. Overview
    html += f"""
            <section class="section" id="overview">
                <h2>1. 개요 및 신호 발생 현황</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>전체 다운로드된 데이터에서 각 신호가 얼마나 자주 발생했는지 통계를 보여줍니다.</p>
                    <p><strong>왜 중요한가요?</strong> 신호 빈도는 실전 활용성과 직결됩니다. 너무 드물면 기회가 적고, 너무 잦으면 정확도가 낮을 수 있습니다.</p>
                    <p><strong>어떻게 활용하나요?</strong> EXTREME 신호는 1% 미만으로 희소해야 하며, STRONG은 2~3%, MODERATE는 5% 내외가 적정합니다.</p>
                </div>
                <h3>📊 매수 신호 발생 빈도</h3>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="label">전체 데이터 포인트</div>
                        <div class="value">{signal_stats['total_bars']:,}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">EXTREME 매수</div>
                        <div class="value">{signal_stats['extreme_buy']}</div>
                        <span class="unit">{signal_stats['extreme_buy']/signal_stats['total_bars']*100:.3f}%</span>
                    </div>
                    <div class="metric-card">
                        <div class="label">STRONG 매수</div>
                        <div class="value">{signal_stats['strong_buy']}</div>
                        <span class="unit">{signal_stats['strong_buy']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                    <div class="metric-card">
                        <div class="label">MODERATE 매수</div>
                        <div class="value">{signal_stats['moderate_buy']}</div>
                        <span class="unit">{signal_stats['moderate_buy']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                </div>
                
                <h3>📉 매도 신호 발생 빈도</h3>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="label">EXTREME 매도</div>
                        <div class="value">{signal_stats['extreme_sell']}</div>
                        <span class="unit">{signal_stats['extreme_sell']/signal_stats['total_bars']*100:.3f}%</span>
                    </div>
                    <div class="metric-card">
                        <div class="label">STRONG 매도</div>
                        <div class="value">{signal_stats['strong_sell']}</div>
                        <span class="unit">{signal_stats['strong_sell']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                    <div class="metric-card">
                        <div class="label">MODERATE 매도</div>
                        <div class="value">{signal_stats['moderate_sell']}</div>
                        <span class="unit">{signal_stats['moderate_sell']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                </div>
                
                <h3>🔍 보조 지표 발생 빈도</h3>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="label">FTD 확정 (Follow Through Day)</div>
                        <div class="value">{signal_stats['ftd_confirmed']}</div>
                        <span class="unit">{signal_stats['ftd_confirmed']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                    <div class="metric-card">
                        <div class="label">고위험 경고</div>
                        <div class="value negative">{signal_stats['risk_high']}</div>
                        <span class="unit">{signal_stats['risk_high']/signal_stats['total_bars']*100:.2f}%</span>
                    </div>
                </div>
            </section>
"""
    
    # 2. Backtest - BUY
    html += """
            <section class="section" id="backtest-buy">
                <h2>2. 매수 신호 백테스트 결과</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>각 매수 신호가 실제로 수익을 냈는지 검증하는 핵심 섹션입니다. 신호 발생 시점에 진입하여 일정 기간 보유했을 때의 성과를 측정합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 아무리 멋진 신호도 실제 수익으로 이어지지 않으면 무용지물입니다. 이 섹션에서 신호의 실전 가치를 검증합니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>승률 60% 이상</strong>이 목표입니다. 50% 이하라면 동전 던지기보다 못하므로 개선이 필수입니다.</li>
                        <li><strong>보유 기간별 차이</strong>를 보면 최적 청산 시점을 알 수 있습니다. 너무 짧으면 이익을 놓치고, 너무 길면 반등에 휘말립니다.</li>
                        <li><strong>Sharpe 비율</strong>은 위험 대비 수익률입니다. 1.0 이상이면 양호, 2.0 이상이면 우수합니다.</li>
                        <li><strong>최대 낙폭(Max DD)</strong>이 -30%를 넘으면 심리적으로 버티기 어렵습니다.</li>
                    </ul>
                </div>
"""
    
    buy_signals = {k: v for k, v in backtest_results.items() if 'BUY' in k}
    for signal_name, holdings in buy_signals.items():
        signal_ko = signal_name.replace('BUY_EXTREME', 'EXTREME 매수').replace('BUY_STRONG', 'STRONG 매수').replace('BUY_MODERATE', 'MODERATE 매수')
        html += f"<h3>{signal_ko} 신호</h3>"
        html += "<table><thead><tr>"
        html += "<th>보유 기간</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th><th>중앙값 수익률</th><th>Sharpe</th><th>최대 낙폭</th></tr></thead><tbody>"
        
        for period in sorted(holdings.keys()):
            stats = holdings[period]
            wr_class = 'positive' if stats['win_rate'] >= 0.6 else 'negative' if stats['win_rate'] < 0.5 else 'neutral'
            pnl_class = 'positive' if stats['avg_pnl'] > 0 else 'negative'
            
            html += f"""<tr>
                <td>{period}일</td>
                <td>{stats['count']}개</td>
                <td class="{wr_class}">{stats['win_rate']*100:.1f}%</td>
                <td class="{pnl_class}">{stats['avg_pnl']*100:+.2f}%</td>
                <td class="{pnl_class}">{stats['median_pnl']*100:+.2f}%</td>
                <td>{stats['sharpe']:.2f}</td>
                <td class="negative">{stats['max_dd']*100:.1f}%</td>
            </tr>"""
        
        html += "</tbody></table>"
    
    html += "</section>"
    
    # 2-2. Backtest - SELL (매도 신호가 있을 때만)
    sell_signals = {k: v for k, v in backtest_results.items() if 'SELL' in k}
    if sell_signals:
        html += """
            <section class="section" id="backtest-sell">
                <h2>3. 매도 신호 백테스트 결과 (공매도 또는 청산)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>매도 신호가 발생했을 때 공매도(Short) 또는 보유 자산 청산 시의 성과를 검증합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 상승장에서만 수익을 내는 전략은 한계가 있습니다. 매도 신호로 하락장에서도 수익을 낼 수 있다면 전천후 전략이 됩니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>매도 신호는 "가격 하락"을 예측</strong>합니다. PnL이 양수라면 실제로 하락했다는 의미입니다.</li>
                        <li><strong>공매도는 위험</strong>하므로, 승률이 매수보다 더 높아야 합니다 (65% 이상 권장).</li>
                        <li><strong>실전 활용:</strong> 승률이 낮다면 공매도 대신 "보유 자산 청산 시그널"로만 활용하는 것이 안전합니다.</li>
                    </ul>
                </div>
"""
    
    for signal_name, holdings in sell_signals.items():
        signal_ko = signal_name.replace('SELL_EXTREME', 'EXTREME 매도').replace('SELL_STRONG', 'STRONG 매도').replace('SELL_MODERATE', 'MODERATE 매도')
        html += f"<h3>{signal_ko} 신호</h3>"
        html += "<table><thead><tr>"
        html += "<th>보유 기간</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th><th>중앙값 수익률</th><th>Sharpe</th><th>최대 낙폭</th></tr></thead><tbody>"
        
        for period in sorted(holdings.keys()):
            stats = holdings[period]
            wr_class = 'positive' if stats['win_rate'] >= 0.65 else 'negative' if stats['win_rate'] < 0.55 else 'neutral'
            pnl_class = 'positive' if stats['avg_pnl'] > 0 else 'negative'
            
            html += f"""<tr>
                <td>{period}일</td>
                <td>{stats['count']}개</td>
                <td class="{wr_class}">{stats['win_rate']*100:.1f}%</td>
                <td class="{pnl_class}">{stats['avg_pnl']*100:+.2f}%</td>
                <td class="{pnl_class}">{stats['median_pnl']*100:+.2f}%</td>
                <td>{stats['sharpe']:.2f}</td>
                <td class="negative">{stats['max_dd']*100:.1f}%</td>
            </tr>"""
        
        html += "</tbody></table>"
    
        html += "</section>"
    
    # 3. 4-Axis Score
    if score_analysis:
        html += """
            <section class="section" id="score">
                <h2>4. 4축 스코어 분해 분석 (Trend/Momentum/Volatility/Context)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>Bottom Score는 4가지 축(Trend, Momentum, Volatility, Context)의 합계입니다. 이 섹션에서는 "어느 축이 실제 승률에 가장 큰 영향을 미치는지" 분해 분석합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 각 축의 실제 기여도를 알아야 가중치를 조정할 수 있습니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>Trend Score가 높을수록</strong> 장기 추세가 강하다는 의미입니다. 상승 추세에서 매수하면 승률이 높습니다.</li>
                        <li><strong>Momentum Score가 높을수록</strong> 단기 모멘텀이 강합니다. 하지만 과열 구간일 수도 있으니 주의가 필요합니다.</li>
                        <li><strong>Volatility Score가 높을수록</strong> 변동성이 크다는 의미입니다. 과도한 변동성은 오히려 위험 신호일 수 있습니다.</li>
                        <li><strong>Context Score가 높을수록</strong> 상황적 요인(FTD, TD, WVF 등)이 일치합니다. 복합 신호는 신뢰도가 높습니다.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> Low 구간 승률이 높다면 해당 축의 가중치를 낮춰도 됩니다. High 구간 승률이 낮다면 과적합(Overfitting) 신호입니다.</p>
                </div>
"""
        
        for axis_name, axis_data in score_analysis.items():
            if axis_name == 'best_combo':
                continue
            
            axis_ko = axis_name  # 이미 한글화됨 (Trend, Momentum 등은 그대로 사용)
            html += f"<h3>{axis_ko} 점수 구간별 성과</h3>"
            html += "<table><thead><tr><th>점수 구간</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th></tr></thead><tbody>"
            
            for bin_label, metrics in axis_data.items():
                wr_class = 'positive' if metrics['win_rate'] >= 0.6 else 'neutral' if metrics['win_rate'] >= 0.5 else 'negative'
                html += f"""<tr>
                    <td>{bin_label}</td>
                    <td>{metrics['count']}개</td>
                    <td class="{wr_class}">{metrics['win_rate']*100:.1f}%</td>
                    <td class="positive">{metrics['avg_pnl']*100:+.2f}%</td>
                </tr>"""
            
            html += "</tbody></table>"
        
        if 'best_combo' in score_analysis:
            combo = score_analysis['best_combo']
            html += f"""
                <div class="highlight-box box-success">
                    <h3>🏆 최강 조합 발견!</h3>
                    <p><strong>Trend 4+ & Context 8+</strong> 조합이 최고 성과를 냈습니다.</p>
                    <p>신호 개수: {combo['count']}개 | 승률: <span class="positive">{combo['win_rate']*100:.1f}%</span> | 평균 수익률: <span class="positive">{combo['avg_pnl']*100:+.2f}%</span></p>
                    <p style="margin-top: 10px;"><strong>논리:</strong> Trend가 강하고(4점+) Context가 매우 높다(8점+)는 것은 "장기 추세가 확실하고 복합 신호도 일치"한다는 의미입니다. 이런 상황에서는 승률이 월등히 높습니다.</p>
                </div>
"""
        
        html += "</section>"
    
    # 4. Components
    if component_analysis:
        html += """
            <section class="section" id="components">
                <h2>5. 핵심 컴포넌트 성능 검증 (FTD / TD / WVF)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>우리 인디케이터는 3가지 핵심 기술적 지표를 사용합니다: <strong>FTD (Follow-Through Day)</strong>, <strong>TD Sequential</strong>, <strong>WVF (Williams Vix Fix)</strong>. 이 섹션에서는 각 지표가 실제로 얼마나 정확한지 검증합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 각 지표의 실제 정확도를 알아야 가중치를 합리적으로 조정할 수 있습니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>FTD Confirmed (1.0pt):</strong> 하락 후 강한 반등이 확정된 날입니다. 승률이 70% 이상이라면 가중치를 2.0pt로 올려도 좋습니다.</li>
                        <li><strong>TD Buy 9 (2.0pt):</strong> 9일 연속 하락을 의미합니다. 단기 반등 가능성이 높지만, 추세 전환까지는 아닙니다.</li>
                        <li><strong>TD Buy 13+ (5.0pt):</strong> 13일+ 연속 하락은 극단적 과매도입니다. 강력한 반등 신호이지만, 너무 드물면 실전 활용이 어렵습니다.</li>
                        <li><strong>WVF Extreme (1.0pt):</strong> 공포 지수가 극단적으로 높은 상태입니다. 하지만 "공포"가 계속될 수도 있으므로, 승률이 50% 미만이라면 가중치를 낮춰야 합니다.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> 승률 70% 이상이면 우수, 50~70%는 보통, 50% 미만이면 개선 필요입니다.</p>
                </div>
"""
        
        html += "<table><thead><tr><th>지표 이름</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th><th>현재 가중치</th></tr></thead><tbody>"
        
        weights = {
            'FTD Confirmed': '1.0pt',
            'TD Buy 9': '2.0pt',
            'TD Buy 13+': '5.0pt',
            'WVF Extreme': '1.0pt',
        }
        
        for comp_name, metrics in component_analysis.items():
            wr_class = 'positive' if metrics['win_rate'] >= 0.7 else 'neutral' if metrics['win_rate'] >= 0.5 else 'negative'
            weight = weights.get(comp_name, 'N/A')
            
            html += f"""<tr>
                <td><strong>{comp_name}</strong></td>
                <td>{metrics['count']}개</td>
                <td class="{wr_class}">{metrics['win_rate']*100:.1f}%</td>
                <td class="positive">{metrics['avg_pnl']*100:+.2f}%</td>
                <td>{weight}</td>
            </tr>"""
        
        html += "</tbody></table></section>"
    
    # 5. VIX Regime
    if vix_analysis:
        html += """
            <section class="section" id="vix">
                <h2>6. VIX 레짐별 효과 검증</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>VIX(변동성 지수)가 높을 때와 낮을 때, 시장 상황이 다릅니다. 우리 인디케이터는 VIX 레짐에 따라 임계값을 조정합니다 (<strong>HIGH: -2점, LOW: +3점</strong>). 이 섹션에서는 이 조정이 실제로 효과가 있는지 검증합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 같은 신호라도 변동성이 다르면 의미가 다릅니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>VIX LOW (VIX < 17):</strong> 시장이 안정적입니다. 이럴 때는 작은 하락도 매수 기회이므로 임계값을 +3점 완화합니다 (18점 → 21점). 즉, 신호가 더 자주 발생합니다.</li>
                        <li><strong>VIX NORMAL (17 ≤ VIX ≤ 25):</strong> 평범한 상황입니다. 조정 없이 기본 임계값(18점)을 사용합니다.</li>
                        <li><strong>VIX HIGH (VIX > 25):</strong> 공포장입니다. 하락이 심하므로 임계값을 -2점 강화합니다 (18점 → 16점). 즉, 신호가 더 자주 발생하지만, 승률이 높아야 정당화됩니다.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> HIGH 레짐 승률이 낮다면 조정을 -2점에서 -1점으로 완화하거나, 반대로 LOW 레짐 승률이 매우 높다면 +3점을 +4점으로 늘려도 됩니다.</p>
                </div>
"""
        
        html += "<table><thead><tr><th>VIX 레짐</th><th>임계값 조정</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th></tr></thead><tbody>"
        
        regime_adjusts = {'LOW': '+3', 'NORMAL': '0', 'HIGH': '-2'}
        regime_desc = {
            'LOW': 'VIX < 17 (안정장)',
            'NORMAL': '17 ≤ VIX ≤ 25 (보통)',
            'HIGH': 'VIX > 25 (공포장)'
        }
        
        for regime_name, metrics in vix_analysis.items():
            adjust = regime_adjusts.get(regime_name, '0')
            desc = regime_desc.get(regime_name, regime_name)
            wr_class = 'positive' if metrics['win_rate'] >= 0.6 else 'neutral'
            
            html += f"""<tr>
                <td><strong>{desc}</strong></td>
                <td>{adjust}점</td>
                <td>{metrics['count']}개</td>
                <td class="{wr_class}">{metrics['win_rate']*100:.1f}%</td>
                <td class="positive">{metrics['avg_pnl']*100:+.2f}%</td>
            </tr>"""
        
        html += "</tbody></table></section>"
    
    # 6. Stage
    if stage_analysis:
        html += """
            <section class="section" id="stage">
                <h2>7. Stage별 타이밍 분석 (시장 사이클)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>시장은 4단계 사이클을 반복합니다: <strong>Stage 1 (축적), Stage 2 (상승), Stage 3 (분산), Stage 4 (하락)</strong>. 이 섹션에서는 어느 Stage에서 매수 신호가 가장 정확한지 분석합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 같은 신호라도 Stage에 따라 성공률이 다릅니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>Stage 1 (축적기):</strong> 하락 후 바닥권에서 횡보합니다. 이 구간에서 매수하면 상승 초기에 진입할 수 있어 승률이 높습니다.</li>
                        <li><strong>Stage 2 (상승기):</strong> 본격적인 상승 추세입니다. 하지만 이미 많이 올랐기 때문에, 매수 신호가 "조정 후 재진입" 타이밍인지 확인이 필요합니다.</li>
                        <li><strong>Stage 3 (분산기):</strong> 고점 부근에서 횡보합니다. 매수 신호가 나와도 위험합니다. 승률이 낮으면 이 Stage에서는 신호를 무시하는 것이 안전합니다.</li>
                        <li><strong>Stage 4 (하락기):</strong> 본격 하락 추세입니다. 매수 신호는 "단기 반등" 가능성이지만, 추세를 거스르므로 위험합니다. 승률이 매우 높지 않으면 진입하지 않는 것이 좋습니다.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> Stage 1과 4에서 승률이 높다면 "역추세 전략"이 유효합니다. Stage 2와 3에서 승률이 높다면 "추세 추종 전략"이 유효합니다.</p>
                </div>
"""
        
        html += "<table><thead><tr><th>Stage</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th></tr></thead><tbody>"
        
        for stage_name, metrics in stage_analysis.items():
            wr_class = 'positive' if metrics['win_rate'] >= 0.65 else 'neutral'
            
            html += f"""<tr>
                <td><strong>{stage_name}</strong></td>
                <td>{metrics['count']}개</td>
                <td class="{wr_class}">{metrics['win_rate']*100:.1f}%</td>
                <td class="positive">{metrics['avg_pnl']*100:+.2f}%</td>
            </tr>"""
        
        html += "</tbody></table></section>"
    
    # 7. False Signals
    if false_analysis and false_analysis.get('patterns'):
        html += """
            <section class="section" id="false">
                <h2>8. 실패 패턴 분석 (왜 틀렸는가?)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>손실이 발생한 거래들을 분석하여 "어떤 공통점이 있는지" 찾아냅니다. 실패에서 배우는 것이 성공보다 중요합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 실패 패턴을 알면 같은 실수를 반복하지 않을 수 있습니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>특정 지표가 손실에 자주 등장</strong>한다면, 그 지표의 가중치를 낮추거나 제거해야 합니다.</li>
                        <li><strong>특정 Stage에서 손실이 집중</strong>된다면, 해당 Stage에서는 진입하지 않는 필터를 추가해야 합니다.</li>
                        <li><strong>Volatility Score가 과도</strong>하게 높을 때 손실이 많다면, 변동성 상한선을 설정해야 합니다.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> 이 섹션의 경고를 무시하지 마세요. 데이터가 직접 말하는 "위험 신호"입니다.</p>
                </div>
"""
        
        html += f"""
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="label">총 손실 거래</div>
                        <div class="value negative">{false_analysis['total_losses']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">총 수익 거래</div>
                        <div class="value positive">{false_analysis['total_wins']}</div>
                    </div>
                    <div class="metric-card">
                        <div class="label">손실률</div>
                        <div class="value neutral">{false_analysis['total_losses']/(false_analysis['total_losses']+false_analysis['total_wins'])*100:.1f}%</div>
                    </div>
                </div>
                
                <h3>⚠️ 손실 거래의 공통 패턴</h3>
"""
        
        for pattern in false_analysis['patterns']:
            html += f'<div class="highlight-box box-warning">[경고] {pattern}</div>'
        
        html += "</section>"
    
    # 8. Optimal Patterns
    if optimal_patterns and optimal_patterns.get('patterns'):
        html += """
            <section class="section" id="patterns">
                <h2>9. 최적 패턴 자동 발견 (고승률 조합)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>머신러닝 기법으로 데이터를 분석하여, "어떤 조합이 가장 높은 승률을 기록했는지" 자동으로 찾아냅니다.</p>
                    <p><strong>왜 중요한가요?</strong> 사람이 찾기 어려운 복잡한 패턴을 발견할 수 있습니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>고승률 패턴</strong>은 실전에서 우선적으로 활용해야 하는 "골든 조합"입니다.</li>
                        <li>패턴이 너무 복잡하면 과적합(Overfitting) 위험이 있으니, 신호 개수가 10개 이상인 패턴만 신뢰하세요.</li>
                        <li><strong>실전 활용:</strong> 이 패턴이 나타날 때는 포지션 크기를 늘리거나, 보유 기간을 길게 가져가도 좋습니다.</li>
                    </ul>
                </div>
"""
        
        for pattern in optimal_patterns['patterns']:
            html += f"""
                <div class="pattern-card">
                    <h3>🎯 {pattern['name']}</h3>
                    <div style="margin-top: 10px;">
                        <span class="badge badge-info">{pattern['count']}개 신호</span>
                        <span class="badge badge-success">승률 {pattern['win_rate']*100:.1f}%</span>
                        <span class="badge badge-info">평균 {pattern['avg_pnl']*100:+.2f}%</span>
                    </div>
                </div>
"""
        
        html += "</section>"
    
    # 9. Threshold Optimization
    if threshold_opt and threshold_opt.get('results'):
        html += """
            <section class="section" id="threshold">
                <h2>10. EXTREME 임계값 최적화 (18점이 최선인가?)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>현재 EXTREME 매수 신호의 임계값은 <strong>18점</strong>입니다. 이 섹션에서는 16점, 17점, 19점, 20점 등 다양한 값을 테스트하여 "어느 값이 가장 높은 승률을 기록하는지" 검증합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 임계값이 너무 낮으면 신호가 많지만 승률이 떨어지고, 너무 높으면 신호가 드물어 기회를 놓칩니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>임계값을 낮추면 (16점, 17점):</strong> 신호 개수는 늘지만, 정확도가 떨어질 수 있습니다. "양"과 "질"의 트레이드오프입니다.</li>
                        <li><strong>임계값을 높이면 (19점, 20점):</strong> 신호는 드물지만, 정확도가 올라갈 수 있습니다. "희소하지만 강력한" 전략입니다.</li>
                        <li><strong>최적값:</strong> 승률이 가장 높은 임계값이 최적입니다. 단, 신호 개수가 10개 미만이면 통계적 신뢰도가 낮으니 주의하세요.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> 최적값이 현재 설정(18점)과 다르다면, Pine Script 코드를 수정하여 EXTREME_BASE 값을 변경하세요.</p>
                </div>
"""
        
        html += "<table><thead><tr><th>임계값</th><th>신호 개수</th><th>승률</th><th>평균 수익률</th><th>상태</th></tr></thead><tbody>"
        
        for result in threshold_opt['results']:
            wr_class = 'positive' if result['win_rate'] >= 0.65 else 'neutral'
            status = "← 현재 설정" if result['threshold'] == 18 else ""
            
            if threshold_opt['best']['threshold'] == result['threshold'] and result['threshold'] != 18:
                status = "⭐ 최적값"
            
            html += f"""<tr>
                <td><strong>{result['threshold']}점</strong></td>
                <td>{result['count']}개</td>
                <td class="{wr_class}">{result['win_rate']*100:.1f}%</td>
                <td class="positive">{result['avg_pnl']*100:+.2f}%</td>
                <td>{status}</td>
            </tr>"""
        
        html += "</tbody></table>"
        
        best = threshold_opt['best']
        if best['threshold'] != 18:
            html += f"""
                <div class="highlight-box box-success">
                    <strong>💡 권장 사항</strong><br>
                    임계값을 <strong>{best['threshold']}점</strong>으로 변경하면 승률이 <strong>{best['win_rate']*100:.1f}%</strong>로 상승합니다.<br>
                    Pine Script에서 EXTREME_BASE = {best['threshold']}로 수정하세요.
                </div>
"""
        else:
            html += """
                <div class="highlight-box box-success">
                    <strong>✅ 현재 설정이 최적입니다</strong><br>
                    18점 설정은 데이터 기반으로 검증된 최적값입니다. 변경 불필요!
                </div>
"""
        
        html += "</section>"
    
    # 10. Final Recommendations
    html += """
            <section class="section" id="recommendations">
                <h2>11. 최종 권장 사항 (종합 개선안)</h2>
                <div class="insight">
                    <strong>📌 이 섹션은 무엇인가요?</strong>
                    <p>앞의 모든 분석 결과를 종합하여, "<strong>실제로 어떻게 개선할 것인가</strong>"에 대한 구체적인 액션 아이템을 제시합니다.</p>
                    <p><strong>왜 중요한가요?</strong> 분석만으로는 의미가 없습니다. 실행 가능한 개선안이 있어야 인디케이터가 발전합니다.</p>
                    <p><strong>논리적 해석:</strong></p>
                    <ul style="margin-left: 20px; margin-top: 8px;">
                        <li><strong>[OK] 성공 항목:</strong> 이미 잘 작동하고 있으므로, 해당 부분을 더 강화하세요.</li>
                        <li><strong>[WARN] 경고 항목:</strong> 문제는 있지만 치명적이진 않습니다. 개선하면 성과가 올라갈 것입니다.</li>
                        <li><strong>[FAIL] 실패 항목:</strong> 반드시 수정해야 합니다. 이대로 두면 손실이 계속됩니다.</li>
                        <li><strong>[INFO] 정보 항목:</strong> 일반적인 개선 제안입니다. 시간이 날 때 검토해보세요.</li>
                    </ul>
                    <p><strong>실전 활용:</strong> 우선순위는 [FAIL] → [WARN] → [OK] → [INFO] 순입니다. FAIL 항목부터 즉시 수정하세요!</p>
                </div>
                <h3>📋 데이터 기반 개선 제안</h3>
"""
    
    recommendations = []
    
    # From component analysis
    if component_analysis:
        if 'FTD Confirmed' in component_analysis:
            ftd_wr = component_analysis['FTD Confirmed']['win_rate']
            if ftd_wr >= 0.7:
                recommendations.append({
                    'type': 'success',
                    'text': f"FTD Confirmed 승률 {ftd_wr*100:.1f}% - 가중치 1.0pt → 2.0pt 상향 검토"
                })
        
        if 'WVF Extreme' in component_analysis:
            wvf_wr = component_analysis['WVF Extreme']['win_rate']
            if wvf_wr < 0.5:
                recommendations.append({
                    'type': 'danger',
                    'text': f"WVF Extreme 승률 {wvf_wr*100:.1f}% - 필터 강화 필요 (과다 발생)"
                })
        
        if 'TD Buy 13+' in component_analysis:
            td13_wr = component_analysis['TD Buy 13+']['win_rate']
            if td13_wr < 0.55:
                recommendations.append({
                    'type': 'warning',
                    'text': f"TD Buy 13+ 승률 {td13_wr*100:.1f}% - 가중치 5.0pt → 3.0pt 하향 검토"
                })
    
    # From VIX analysis
    if vix_analysis and 'HIGH' in vix_analysis:
        high_wr = vix_analysis['HIGH']['win_rate']
        if high_wr >= 0.65:
            recommendations.append({
                'type': 'info',
                'text': f"VIX HIGH 레짐 승률 {high_wr*100:.1f}% - 임계값 완화 효과 확인 (-2점 → -3점 검토)"
            })
    
    # From threshold optimization
    if threshold_opt and threshold_opt.get('best'):
        best = threshold_opt['best']
        if best['threshold'] != 18 and best['win_rate'] > 0.65:
            recommendations.append({
                'type': 'success',
                'text': f"EXTREME 임계값 {best['threshold']}점 최적 (승률 {best['win_rate']*100:.1f}%)"
            })
    
    # From false signals
    if false_analysis and false_analysis.get('patterns'):
        for pattern in false_analysis['patterns'][:2]:  # Top 2
            recommendations.append({
                'type': 'warning',
                'text': f"손실 패턴 발견: {pattern}"
            })
    
    # General improvements
    recommendations.extend([
        {
            'type': 'info',
            'text': "Context Score 재분배 권장: TD 비중 축소, FTD 비중 확대"
        },
        {
            'type': 'info',
            'text': "Stage 1/4 진입 시점에 신호 가중치 추가 부여 검토"
        },
        {
            'type': 'info',
            'text': "변동성 Tier별 최적 보유 기간 차별화 (High: 10일, Low: 20일)"
        },
    ])
    
    for rec in recommendations:
        box_class = f"box-{rec['type']}"
        icon = {'success': '[OK]', 'warning': '[WARN]', 'danger': '[FAIL]', 'info': '[INFO]'}[rec['type']]
        html += f'<div class="highlight-box {box_class}">{icon} {rec["text"]}</div>'
    
    html += """
            </section>
        </div>
        
        <div class="footer">
            <p><strong>RYAION v19.1 유니버설 인디케이터</strong></p>
            <p>심층 성능 분석 보고서 - 데이터 기반 전략 개선 시스템</p>
            <p style="margin-top: 10px; opacity: 0.8;">이 보고서는 실제 다운로드된 시장 데이터를 기반으로 자동 생성되었습니다.</p>
            <p style="margin-top: 5px; opacity: 0.7; font-size: 12px;">© 2025 RYAION Project. All data-driven insights.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

# ============================================================================
# 메인 실행
# ============================================================================

def main(filter_asset_class=None, filter_sub_category=None):
    """
    메인 분석 함수
    
    Args:
        filter_asset_class: 필터링할 자산군 (예: 'ETF')
        filter_sub_category: 필터링할 세부 카테고리 (예: '주식형 ETF')
    """
    print("="*80)
    print("RYAION v19.1 Universal Indicator")
    print("Deep Performance Analyzer")
    if filter_asset_class:
        print(f"Filter: {filter_asset_class}" + (f" > {filter_sub_category}" if filter_sub_category else ""))
    print("="*80)
    
    # 데이터 로드
    df_list, ticker_categories = load_all_csvs()
    
    if not df_list:
        print("\n[ERROR] No data to analyze!")
        print("Please run START_HERE.bat first to download data.")
        input("\nPress Enter to exit...")
        return
    
    # 필터링 적용
    if filter_asset_class:
        original_count = len(df_list)
        if filter_sub_category:
            df_list = [df for df in df_list if df['asset_class'].iloc[0] == filter_asset_class and df['sub_category'].iloc[0] == filter_sub_category]
            filter_label = f"{filter_asset_class}_{filter_sub_category}"
        else:
            df_list = [df for df in df_list if df['asset_class'].iloc[0] == filter_asset_class]
            filter_label = filter_asset_class
        
        print(f"\n[INFO] Filter applied: {original_count} → {len(df_list)} tickers")
        
        if not df_list:
            print("\n[ERROR] No data matches the filter!")
            input("\nPress Enter to exit...")
            return
    else:
        filter_label = "All"
    
    # 분석 시작
    print(f"\n{'='*80}")
    print(f"Analysis started: {len(df_list)} tickers, {sum(len(df) for df in df_list):,} data points")
    print(f"{'='*80}")
    
    # 0. 자산군별 요약 분석
    asset_summary = analyze_by_asset_class(df_list, ticker_categories)
    
    # 1. 신호 통계
    signal_stats = analyze_signals(df_list)
    
    # 2. 기본 백테스트
    backtest_results = run_basic_backtest(df_list)
    
    # 3. 4축 스코어 분해
    score_analysis = analyze_score_components(df_list, backtest_results)
    
    # 4. 컴포넌트 분석
    component_analysis = analyze_components(df_list, backtest_results)
    
    # 5. VIX 레짐
    vix_analysis = analyze_vix_regime(df_list, backtest_results)
    
    # 6. Stage 타이밍
    stage_analysis = analyze_stage_timing(df_list, backtest_results)
    
    # 7. False Signal
    false_analysis = analyze_false_signals(df_list, backtest_results)
    
    # 8. 최적 패턴
    optimal_patterns = find_optimal_patterns(df_list, backtest_results)
    
    # 9. 임계값 최적화
    threshold_opt = optimize_thresholds(df_list)
    
    # HTML 보고서 생성
    print(f"\n{'='*80}")
    print("[INFO] Generating comprehensive report...")
    print(f"{'='*80}")
    
    html_content = generate_html_report(
        asset_summary,
        ticker_categories,
        signal_stats,
        backtest_results,
        score_analysis,
        component_analysis,
        vix_analysis,
        stage_analysis,
        false_analysis,
        optimal_patterns,
        threshold_opt,
    )
    
    # 파일명에 필터 정보 포함
    filename_prefix = f"deep_analysis_{filter_label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_path = REPORT_DIR / f"{filename_prefix}.html"
    report_path.write_text(html_content, encoding='utf-8')
    
    print(f"\n[OK] Report generated successfully!")
    print(f"[FILE] {report_path}")
    
    # JSON 저장 (안전하게 변환)
    def safe_convert(obj):
        """중첩 딕셔너리를 안전하게 JSON 직렬화 가능한 형태로 변환"""
        if isinstance(obj, dict):
            return {k: safe_convert(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [safe_convert(item) for item in obj]
        elif isinstance(obj, (int, float, np.number)):
            return float(obj)
        elif isinstance(obj, (str, bool, type(None))):
            return obj
        elif hasattr(obj, 'to_dict'):
            return safe_convert(obj.to_dict())
        else:
            return str(obj)
    
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'signal_stats': safe_convert(signal_stats),
        'score_analysis': safe_convert(score_analysis),
        'component_analysis': safe_convert(component_analysis),
        'vix_analysis': safe_convert(vix_analysis),
        'stage_analysis': safe_convert(stage_analysis),
        'false_analysis': safe_convert(false_analysis),
        'optimal_patterns': safe_convert(optimal_patterns),
        'threshold_opt': safe_convert(threshold_opt),
    }
    
    json_path = REPORT_DIR / f"deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"[JSON] {json_path}")
    
    # 브라우저 열기
    print(f"\n{'='*80}")
    print("[INFO] Opening report in browser...")
    print(f"{'='*80}")
    
    os.system(f'start "" "{report_path.absolute()}"')
    
    print("\n[OK] Deep analysis complete!")
    print("\nReport Contents:")
    print("  1. 4-Axis Score Decomposition (which axis is most important)")
    print("  2. Component Performance (FTD/TD/WVF actual accuracy)")
    print("  3. VIX Regime Effect Verification")
    print("  4. Stage Timing Analysis")
    print("  5. False Signal Patterns")
    print("  6. Optimal Pattern Discovery")
    print("  7. Threshold Optimization")
    print("  8. Comprehensive Improvement Recommendations")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    import sys
    
    # Command line arguments 처리
    filter_asset = None
    filter_sub = None
    
    if len(sys.argv) > 1:
        filter_asset = sys.argv[1]
        if len(sys.argv) > 2:
            filter_sub = sys.argv[2]
    
    try:
        main(filter_asset_class=filter_asset, filter_sub_category=filter_sub)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
