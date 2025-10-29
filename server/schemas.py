"""
VMSI-SDM Pydantic Schemas
TradingView Webhook 데이터 검증 및 타입 정의
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class MacroFeatures(BaseModel):
    """매크로 지표 피처"""
    vix: float = Field(..., description="VIX 지수")
    dxy_trend: str = Field(..., description="DXY 트렌드 (up/down/flat)")
    us10y_trend: str = Field(..., description="미국 10년물 트렌드")
    hyg_ief: str = Field(..., description="HYG/IEF 비율 상태 (bull/bear)")


class Features(BaseModel):
    """신호 발생 시 피처 세트"""
    trendScore: float = Field(..., ge=0, le=100, description="트렌드 스코어 (0-100)")
    prob: float = Field(..., ge=0, le=1, description="확률 (0-1)")
    ema20_above_50: bool = Field(..., description="EMA20 > EMA50 여부")
    rsi: float = Field(..., ge=0, le=100, description="RSI 값")
    vol_mult: float = Field(..., ge=0, description="거래량 배수")
    vcp_ratio: float = Field(..., ge=0, le=1, description="VCP 비율")
    dist_ath: float = Field(..., ge=0, description="ATH 대비 거리")
    macro: MacroFeatures


class Parameters(BaseModel):
    """지표 파라미터"""
    ema1: int = Field(20, description="EMA1 기간")
    ema2: int = Field(50, description="EMA2 기간")
    rsi: int = Field(14, description="RSI 기간")
    vcp: int = Field(20, description="VCP 기간")
    alpha: float = Field(0.8, description="TrendScore 가중치")
    beta: float = Field(0.35, description="RSI 가중치")
    gamma: float = Field(0.7, description="VolMult 가중치")
    delta: float = Field(0.6, description="VCP 가중치")
    epsilon: float = Field(0.8, description="Macro 가중치")


class TradingViewAlert(BaseModel):
    """TradingView Webhook Alert 페이로드"""
    symbol: str = Field(..., description="심볼 (AAPL, BTCUSD 등)")
    tf: str = Field(..., description="타임프레임 (5, 15, 1D 등)")
    t: str = Field(..., description="타임스탬프")
    signal: str = Field(..., description="신호 (BUY/SELL/WATCH_UP/WATCH_DOWN)")
    features: Features
    params: Parameters
    
    @validator('signal')
    def validate_signal(cls, v):
        allowed = ['BUY', 'SELL', 'WATCH_UP', 'WATCH_DOWN']
        if v not in allowed:
            raise ValueError(f'Signal must be one of {allowed}')
        return v
    
    @validator('t')
    def validate_timestamp(cls, v):
        """타임스탬프를 datetime으로 변환 가능한지 확인"""
        try:
            # Pine에서 보내는 형식: 밀리초 timestamp
            int(v)
        except:
            raise ValueError('Invalid timestamp format')
        return v


class SignalResponse(BaseModel):
    """Webhook 응답"""
    status: str = Field("success", description="처리 상태")
    signal_id: Optional[int] = Field(None, description="저장된 신호 ID")
    message: str = Field("Signal received and stored", description="메시지")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="수신 시각")


class LabelResult(BaseModel):
    """라벨링 결과"""
    signal_id: int
    fwd_n: int = Field(..., description="Forward N bars")
    fwd_ret: float = Field(..., description="Forward return")
    broke_high: bool = Field(..., description="고가 돌파 여부")
    broke_low: bool = Field(..., description="저가 이탈 여부")


class ExperimentResult(BaseModel):
    """실험 결과"""
    run_id: str = Field(..., description="실험 실행 ID")
    params: Dict[str, Any] = Field(..., description="파라미터 세트")
    metrics: Dict[str, float] = Field(..., description="성능 지표")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시각")



