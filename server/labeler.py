"""
VMSI-SDM Labeler
신호 발생 후 미래 수익률 및 결과를 계산하는 모듈
"""

import os
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from server.db import Signal, Label


class MarketDataLabeler:
    """시장 데이터 기반 라벨러"""
    
    def __init__(self, provider: str = "yahoo"):
        """
        Args:
            provider: 데이터 제공자 (yahoo, polygon 등)
        """
        self.provider = provider
        self.forward_windows = [3, 5, 10, 20]  # N봉 후 결과 확인
    
    def fetch_ohlc(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d") -> pd.DataFrame:
        """
        OHLC 데이터 가져오기
        
        Args:
            symbol: 심볼 (AAPL, BTCUSD 등)
            start_date: 시작일
            end_date: 종료일
            interval: 타임프레임 (1d, 1h, 5m 등)
        
        Returns:
            OHLC DataFrame
        """
        try:
            if self.provider == "yahoo":
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, interval=interval)
                return df
            else:
                # 추후 Polygon, Binance 등 추가 가능
                raise NotImplementedError(f"Provider {self.provider} not implemented")
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_forward_return(self, entry_price: float, future_prices: pd.DataFrame, n: int) -> Tuple[float, bool, bool]:
        """
        N봉 후 수익률 및 고가/저가 돌파 여부 계산
        
        Args:
            entry_price: 진입가
            future_prices: 미래 N봉의 OHLC 데이터
            n: 확인할 봉 개수
        
        Returns:
            (forward_return, broke_high, broke_low)
        """
        if len(future_prices) < n:
            return 0.0, False, False
        
        # N봉 후 종가
        future_close = future_prices.iloc[n-1]['Close'] if n <= len(future_prices) else future_prices.iloc[-1]['Close']
        fwd_ret = (future_close - entry_price) / entry_price
        
        # N봉 내 최고가/최저가
        slice_data = future_prices.iloc[:n]
        high_max = slice_data['High'].max()
        low_min = slice_data['Low'].min()
        
        # 고가 돌파: 진입가 대비 +3% 이상
        broke_high = (high_max - entry_price) / entry_price > 0.03
        
        # 저가 이탈: 진입가 대비 -3% 이상
        broke_low = (entry_price - low_min) / entry_price > 0.03
        
        return fwd_ret, broke_high, broke_low
    
    def label_signal(self, db: Session, signal: Signal) -> List[Label]:
        """
        신호에 대한 라벨 생성
        
        Args:
            db: DB 세션
            signal: 라벨링할 신호
        
        Returns:
            생성된 Label 리스트
        """
        # 신호 발생 시각
        ts = datetime.fromtimestamp(int(signal.ts) / 1000)  # 밀리초 → 초
        
        # 데이터 가져오기 (신호 이후 30봉 정도)
        end_date = ts + timedelta(days=30)
        interval = self._convert_tf_to_yf_interval(signal.tf)
        
        df = self.fetch_ohlc(signal.symbol, ts, end_date, interval)
        
        if df.empty:
            print(f"⚠️  No data for {signal.symbol} from {ts}")
            return []
        
        # 진입가 (신호 발생 봉의 종가)
        entry_price = df.iloc[0]['Close'] if len(df) > 0 else signal.bar_c or 0
        
        # 신호에 OHLC 보강
        if len(df) > 0:
            signal.bar_o = float(df.iloc[0]['Open'])
            signal.bar_h = float(df.iloc[0]['High'])
            signal.bar_l = float(df.iloc[0]['Low'])
            signal.bar_c = float(df.iloc[0]['Close'])
            db.commit()
        
        # 각 forward window에 대해 라벨 생성
        labels = []
        for n in self.forward_windows:
            fwd_ret, broke_high, broke_low = self.calculate_forward_return(entry_price, df, n)
            
            label = Label(
                signal_id=signal.id,
                fwd_n=n,
                fwd_ret=fwd_ret,
                broke_high=broke_high,
                broke_low=broke_low
            )
            db.add(label)
            labels.append(label)
        
        db.commit()
        print(f"[OK] Labeled signal {signal.id} ({signal.symbol} {signal.signal}) with {len(labels)} windows")
        
        return labels
    
    def label_all_unlabeled(self, db: Session, limit: int = 100) -> int:
        """
        라벨이 없는 모든 신호에 대해 라벨링 수행
        
        Args:
            db: DB 세션
            limit: 한 번에 처리할 최대 개수
        
        Returns:
            라벨링된 신호 개수
        """
        # 라벨이 없는 신호 조회
        unlabeled_signals = db.query(Signal).filter(~Signal.labels.any()).limit(limit).all()
        
        count = 0
        for signal in unlabeled_signals:
            try:
                self.label_signal(db, signal)
                count += 1
            except Exception as e:
                print(f"❌ Error labeling signal {signal.id}: {e}")
        
        return count
    
    def _convert_tf_to_yf_interval(self, tf: str) -> str:
        """
        TradingView 타임프레임을 yfinance interval로 변환
        
        Args:
            tf: TradingView 타임프레임 (5, 15, 1D 등)
        
        Returns:
            yfinance interval (5m, 15m, 1d 등)
        """
        mapping = {
            "1": "1m",
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "1H": "1h",
            "4H": "4h",
            "1D": "1d",
            "1W": "1wk",
            "1M": "1mo"
        }
        return mapping.get(tf, "1d")


# ─────────────── 유틸리티 함수 ───────────────

def label_recent_signals(db: Session, days_back: int = 30) -> int:
    """
    최근 N일간의 신호에 대해 라벨링 수행
    
    Args:
        db: DB 세션
        days_back: 과거 며칠치 신호를 라벨링할지
    
    Returns:
        라벨링된 신호 개수
    """
    labeler = MarketDataLabeler()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    recent_signals = db.query(Signal).filter(Signal.created_at >= cutoff_date).all()
    
    count = 0
    for signal in recent_signals:
        # 이미 라벨이 있는 경우 스킵
        if db.query(Label).filter(Label.signal_id == signal.id).count() > 0:
            continue
        
        try:
            labeler.label_signal(db, signal)
            count += 1
        except Exception as e:
            print(f"❌ Error labeling signal {signal.id}: {e}")
    
    return count


if __name__ == "__main__":
    # 테스트용
    from server.db import SessionLocal, init_db
    
    init_db()
    db = SessionLocal()
    
    print("🔄 Labeling unlabeled signals...")
    count = MarketDataLabeler().label_all_unlabeled(db)
    print(f"✓ Labeled {count} signals")
    
    db.close()

