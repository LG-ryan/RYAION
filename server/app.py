"""
VMSI-SDM FastAPI Webhook Server
TradingView 알럿을 수신하고 DB에 저장하는 메인 서버
"""

import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import uvicorn

from server.db import get_db, init_db, Signal, Label, Experiment
from server.schemas import TradingViewAlert, SignalResponse, LabelResult
from server.labeler import MarketDataLabeler

# FastAPI 앱 초기화
app = FastAPI(
    title="VMSI-SDM Webhook Server",
    description="TradingView 신호 수신 및 자가학습 시스템",
    version="2.0.0"
)

# CORS 설정 (Streamlit 대시보드와 통신)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라벨러 인스턴스
labeler = MarketDataLabeler()


# ─────────────── Startup Event ───────────────

@app.on_event("startup")
def startup_event():
    """서버 시작 시 DB 초기화"""
    init_db()
    print("[VMSI-SDM] Server Started")


# ─────────────── Webhook Endpoints ───────────────

@app.post("/alert", response_model=SignalResponse)
async def receive_alert(
    alert: TradingViewAlert,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    TradingView Webhook 알럿 수신 (v2.1 - Simplified)
    
    - **symbol**: 심볼 (SPX, AAPL 등)
    - **action**: BUY, SELL
    - **trend_score**, **prob**, **rsi** 등: 단순화된 flat 구조
    """
    try:
        # 신호 저장 (v2.1 simplified structure)
        features_json = {
            "trend_score": alert.trend_score,
            "prob": alert.prob,
            "rsi": alert.rsi,
            "vol_mult": alert.vol_mult,
            "vcp_ratio": alert.vcp_ratio,
            "dist_ath": alert.dist_ath,
            "ema1": alert.ema1,
            "ema2": alert.ema2,
            "bar_state": alert.bar_state,
            "fast_mode": alert.fast_mode,
            "realtime_macro": alert.realtime_macro,
            "version": alert.version
        }
        
        signal = Signal(
            ts=str(alert.ts_unix),
            symbol=alert.symbol,
            tf=alert.timeframe,
            signal=alert.action,
            features_json=features_json,
            params_json={}  # Params는 features에 포함
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        # 백그라운드에서 라벨링 수행 (비동기)
        if alert.action in ["BUY", "SELL"]:
            background_tasks.add_task(labeler.label_signal, db, signal)
        
        return SignalResponse(
            status="success",
            signal_id=signal.id,
            message=f"Signal saved"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing alert: {str(e)}")


@app.get("/")
def root():
    """Health check"""
    return {
        "status": "running",
        "service": "VMSI-SDM Webhook Server",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ─────────────── Data Endpoints ───────────────

@app.get("/signals", response_model=List[dict])
def get_signals(
    limit: int = 100,
    signal_type: str = None,
    symbol: str = None,
    db: Session = Depends(get_db)
):
    """
    저장된 신호 조회
    
    - **limit**: 조회할 최대 개수
    - **signal_type**: 필터 (BUY, SELL, WATCH_UP, WATCH_DOWN)
    - **symbol**: 심볼 필터
    """
    query = db.query(Signal)
    
    if signal_type:
        query = query.filter(Signal.signal == signal_type.upper())
    
    if symbol:
        query = query.filter(Signal.symbol == symbol.upper())
    
    signals = query.order_by(Signal.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "ts": s.ts,
            "symbol": s.symbol,
            "tf": s.tf,
            "signal": s.signal,
            "features": s.features_json,
            "params": s.params_json,
            "created_at": s.created_at.isoformat()
        }
        for s in signals
    ]


@app.get("/signals/{signal_id}/labels", response_model=List[LabelResult])
def get_signal_labels(signal_id: int, db: Session = Depends(get_db)):
    """
    특정 신호의 라벨 조회
    
    - **signal_id**: 신호 ID
    """
    labels = db.query(Label).filter(Label.signal_id == signal_id).all()
    
    if not labels:
        raise HTTPException(status_code=404, detail="No labels found for this signal")
    
    return [
        LabelResult(
            signal_id=label.signal_id,
            fwd_n=label.fwd_n,
            fwd_ret=label.fwd_ret,
            broke_high=label.broke_high,
            broke_low=label.broke_low
        )
        for label in labels
    ]


@app.post("/labels/generate")
def generate_labels(limit: int = 100, db: Session = Depends(get_db)):
    """
    라벨이 없는 신호들에 대해 라벨 생성
    
    - **limit**: 한 번에 처리할 최대 개수
    """
    count = labeler.label_all_unlabeled(db, limit)
    return {
        "status": "success",
        "labeled_count": count,
        "message": f"Labeled {count} signals"
    }


@app.get("/experiments", response_model=List[dict])
def get_experiments(limit: int = 20, db: Session = Depends(get_db)):
    """
    실험 결과 조회
    
    - **limit**: 조회할 최대 개수
    """
    experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": exp.id,
            "run_id": exp.run_id,
            "params": exp.params,
            "metrics": exp.metrics,
            "created_at": exp.created_at.isoformat()
        }
        for exp in experiments
    ]


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    전체 통계 조회
    """
    total_signals = db.query(Signal).count()
    total_labels = db.query(Label).count()
    total_experiments = db.query(Experiment).count()
    
    buy_signals = db.query(Signal).filter(Signal.signal == "BUY").count()
    sell_signals = db.query(Signal).filter(Signal.signal == "SELL").count()
    
    return {
        "total_signals": total_signals,
        "total_labels": total_labels,
        "total_experiments": total_experiments,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "watch_signals": total_signals - buy_signals - sell_signals
    }


# ─────────────── Main ───────────────

if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    
    uvicorn.run(
        "server.app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

