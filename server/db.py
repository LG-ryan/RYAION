"""
VMSI-SDM Database Models & Session Management
SQLAlchemy ORM 모델 정의
"""

import os
from typing import Generator
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, JSON, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vmsi_sdm.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ─────────────── Models ───────────────

class Signal(Base):
    """수신된 신호 저장"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    ts = Column(String, nullable=False, index=True)  # TradingView timestamp
    symbol = Column(String, nullable=False, index=True)
    tf = Column(String, nullable=False)  # timeframe
    signal = Column(String, nullable=False, index=True)  # BUY/SELL/WATCH_UP/WATCH_DOWN
    
    # JSON으로 저장
    features_json = Column(JSON, nullable=False)
    params_json = Column(JSON, nullable=False)
    
    # OHLC 보강 데이터 (labeler가 채움)
    bar_o = Column(Float, nullable=True)
    bar_h = Column(Float, nullable=True)
    bar_l = Column(Float, nullable=True)
    bar_c = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    labels = relationship("Label", back_populates="signal", cascade="all, delete-orphan")


class Label(Base):
    """미래 결과 라벨"""
    __tablename__ = "labels"
    
    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)
    
    fwd_n = Column(Integer, nullable=False)  # 3, 5, 10, 20
    fwd_ret = Column(Float, nullable=False)  # 수익률
    broke_high = Column(Boolean, nullable=False)  # 고가 돌파 여부
    broke_low = Column(Boolean, nullable=False)  # 저가 이탈 여부
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    signal = relationship("Signal", back_populates="labels")


class Experiment(Base):
    """Optuna 실험 결과"""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, nullable=False, index=True)
    
    params = Column(JSON, nullable=False)  # 최적화된 파라미터
    metrics = Column(JSON, nullable=False)  # PF, MDD, PSU/PSD 등
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = relationship("Report", back_populates="experiment", cascade="all, delete-orphan")


class Report(Base):
    """실험 리포트"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    
    path = Column(String, nullable=False)  # 리포트 파일 경로
    notes = Column(Text, nullable=True)  # 추가 메모
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    experiment = relationship("Experiment", back_populates="reports")


# ─────────────── Database Utilities ───────────────

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: DB 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 초기화 (테이블 생성)"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database initialized")


def reset_db():
    """데이터베이스 초기화 (테이블 삭제 후 재생성) - 개발용"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[OK] Database reset")


if __name__ == "__main__":
    # 직접 실행 시 DB 초기화
    init_db()

