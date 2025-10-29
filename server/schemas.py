"""
VMSI-SDM Pydantic Schemas
TradingView Webhook 데이터 검증 및 타입 정의 (v2.1 - Simplified)
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TradingViewAlert(BaseModel):
    """TradingView Webhook Alert 페이로드 (v2.1 - Simplified)"""
    ts_unix: int = Field(..., description="Unix timestamp (milliseconds)")
    symbol: str = Field(..., description="심볼 (SPX, AAPL 등)")
    timeframe: str = Field(..., description="타임프레임 (1D, 4H 등)")
    action: str = Field(..., description="신호 (BUY/SELL)")
    price: float = Field(..., description="가격")
    trend_score: float = Field(..., ge=0, le=100, description="트렌드 스코어 (0-100)")
    prob: float = Field(..., ge=0, le=1, description="확률 (0-1)")
    rsi: float = Field(..., ge=0, le=100, description="RSI 값")
    vol_mult: float = Field(..., ge=0, description="거래량 배수")
    vcp_ratio: float = Field(..., ge=0, le=1, description="VCP 비율")
    dist_ath: float = Field(..., ge=0, description="ATH 대비 거리")
    ema1: float = Field(..., description="EMA1 값")
    ema2: float = Field(..., description="EMA2 값")
    bar_state: str = Field(..., description="봉 상태 (close)")
    fast_mode: bool = Field(..., description="빠른 모드 여부")
    realtime_macro: bool = Field(..., description="실시간 매크로 사용 여부")
    version: str = Field(..., description="Indicator 버전")


class SignalResponse(BaseModel):
    """신호 저장 응답"""
    status: str = "success"
    signal_id: int
    message: str = "Signal saved"


class LabelResult(BaseModel):
    """레이블 결과"""
    label_id: int
    signal_id: int
    forward_period: int
    return_pct: float
    max_favorable: float
    max_adverse: float
    created_at: datetime
