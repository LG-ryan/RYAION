"""
VMSI-SDM Streamlit Dashboard (Dark Mode)
실시간 신호 모니터링 및 A/B 테스트 비교 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Streamlit Cloud Secrets를 환경변수로 설정 (로컬에서는 스킵)
try:
    if "DATABASE_URL" in st.secrets:
        os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]
except FileNotFoundError:
    # 로컬 환경: SQLite 사용 (DATABASE_URL 불필요)
    pass

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.db import SessionLocal, Signal, Label, Experiment
from learner.preset import PresetManager
from learner.metrics import PerformanceMetrics


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 페이지 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.set_page_config(
    page_title="VMSI-SDM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# UX/UI 개선 다크모드 CSS (v3.0 - 2025-10-29 전면 개선)
st.markdown("""
<style>
    /* ════════════════════════════════════════════════════════
       VMSI-SDM Dashboard - Dark Mode v3.0 (Professional UX)
    ════════════════════════════════════════════════════════ */
    
    /* ──── 1. 전체 레이아웃 ──── */
    .main {
        background-color: #0e1117;
        color: #e6edf3;
        padding: 2rem;
    }
    
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background-color: #0e1117;
    }
    
    /* ──── 2. 타이포그래피 (통일된 폰트 계층) ──── */
    * {
        font-family: 'Inter', 'Pretendard', 'Segoe UI', 'Malgun Gothic', 'Arial', sans-serif !important;
    }
    
    h1 {
        color: #58a6ff !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.8rem !important;
        letter-spacing: -0.02em;
    }
    
    h2 {
        color: #79c0ff !important;
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #21262d;
    }
    
    h3 {
        color: #a5d6ff !important;
        font-size: 1.35rem !important;
        font-weight: 600 !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    h4 {
        color: #c9d1d9 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.6rem !important;
    }
    
    p, span, div, label {
        color: #e6edf3 !important;
        font-size: 0.95rem !important;
        line-height: 1.6;
    }
    
    /* ──── 3. 메트릭 카드 (개선된 시각적 계층) ──── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        border-color: #484f58;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #58a6ff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #9aa2af !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    
    /* ──── 4. 버튼 (프로페셔널 스타일) ──── */
    .stButton button {
        background: linear-gradient(135deg, #1f6feb 0%, #1a5bdb 100%);
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        border: none;
        box-shadow: 0 2px 8px rgba(31, 111, 235, 0.25);
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #1a56db 0%, #1548c4 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.35);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    /* ──── 5. 사이드바 ──── */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    [data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
    
    /* ──── 6. 탭 (깔끔한 디자인) ──── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
        padding: 0;
        border-bottom: 2px solid #21262d;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #9aa2af !important;
        padding: 0.75rem 1.5rem;
        border-radius: 0;
        transition: all 0.2s ease;
        background: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #c9d1d9 !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: transparent !important;
        color: #58a6ff !important;
        border-bottom: 3px solid #1f6feb !important;
    }
    
    /* ──── 7. 데이터프레임 (테이블 스타일 개선) ──── */
    [data-testid="stDataFrame"] {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] * {
        color: #e6edf3 !important;
        font-size: 0.9rem !important;
    }
    
    thead tr th {
        background-color: #161b22 !important;
        color: #9aa2af !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #21262d !important;
        padding: 0.75rem !important;
    }
    
    tbody tr {
        background-color: #0d1117 !important;
        border-bottom: 1px solid #21262d !important;
        transition: background-color 0.15s ease;
    }
    
    tbody tr:hover {
        background-color: #161b22 !important;
    }
    
    tbody td {
        padding: 0.75rem !important;
    }
    
    /* ──── 8. 입력 필드 ──── */
    input, textarea, select {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
        padding: 0.6rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease;
    }
    
    input:focus, textarea:focus, select:focus {
        border-color: #1f6feb !important;
        outline: none;
        box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.2);
    }
    
    /* ──── 9. 정보 박스 (SVG 아이콘 스타일) ──── */
    .info-box {
        background-color: rgba(13, 65, 157, 0.15);
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 3px solid #1f6feb;
        margin: 1rem 0;
        color: #e6edf3 !important;
    }
    
    .success-box {
        background-color: rgba(15, 83, 35, 0.15);
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 3px solid #3fb950;
        margin: 1rem 0;
        color: #e6edf3 !important;
    }
    
    .warning-box {
        background-color: rgba(108, 57, 6, 0.15);
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 3px solid #f85149;
        margin: 1rem 0;
        color: #e6edf3 !important;
    }
    
    /* ──── 10. SVG 아이콘 스타일 ──── */
    .icon-inline {
        display: inline-block;
        width: 1.2em;
        height: 1.2em;
        vertical-align: text-bottom;
        margin-right: 0.4em;
    }
    
    /* ──── 11. 섹션 헤더 스타일 ──── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #21262d;
    }
    
    /* ──── 12. 카드 컨테이너 ──── */
    .card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* ──── 13. 구분선 ──── */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #21262d;
    }
    
    /* ──── 14. Expander ──── */
    [data-testid="stExpander"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }
    
    /* ──── 15. 접근성 ──── */
    *:focus-visible {
        outline: 2px solid #58a6ff;
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 제목
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.title("VMSI-SDM Dashboard")
st.markdown("**자가학습형 TradingView 지표 모니터링 시스템**")
st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 사이드바
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.sidebar.header("설정")

days_back = st.sidebar.slider("조회 기간 (일)", 1, 90, 30)

signal_filter = st.sidebar.multiselect(
    "신호 타입",
    ["BUY", "SELL", "WATCH_UP", "WATCH_DOWN"],
    default=["BUY", "SELL"]
)

symbol_filter = st.sidebar.text_input("심볼 필터 (예: AAPL)", "")

if st.sidebar.button("새로고침"):
    st.rerun()

# ──────────────────────────────────────
# CSV 업로드 섹션
# ──────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.header("📤 데이터 업로드")

uploaded_file = st.sidebar.file_uploader(
    "CSV 파일 업로드 (TradingView Export)",
    type=['csv'],
    help="TradingView에서 내보낸 CSV 파일을 업로드하여 실제 데이터를 추가하세요."
)

if uploaded_file is not None:
    if st.sidebar.button("CSV 임포트 시작", type="primary"):
        with st.spinner("CSV 파일 처리 중..."):
            try:
                # CSV 임시 저장
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # 임포트 스크립트 실행
                import subprocess
                result = subprocess.run(
                    [
                        "python", 
                        "tools/import_real_csv.py", 
                        "--csv", tmp_path,
                        "--symbol", "SPX",
                        "--timeframe", "1W",
                        "--server", "http://localhost:8000/alert"
                    ],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent.parent
                )
                
                # 결과 표시
                if result.returncode == 0:
                    st.sidebar.success("✅ CSV 임포트 완료!")
                    st.sidebar.info(result.stdout)
                else:
                    st.sidebar.error(f"❌ 임포트 실패: {result.stderr}")
                
                # 임시 파일 삭제
                os.unlink(tmp_path)
                
            except Exception as e:
                st.sidebar.error(f"오류 발생: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 데이터 로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data(ttl=60)
def load_signals(days_back: int, signal_types: list, symbol: str = ""):
    """신호 데이터 로드"""
    db = SessionLocal()
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    query = db.query(Signal).filter(Signal.created_at >= cutoff_date)
    
    if signal_types:
        query = query.filter(Signal.signal.in_(signal_types))
    
    if symbol:
        query = query.filter(Signal.symbol.contains(symbol.upper()))
    
    signals = query.order_by(Signal.created_at.desc()).all()
    
    data = []
    for s in signals:
        features = s.features_json
        labels = {label.fwd_n: label for label in s.labels}
        
        data.append({
            'id': s.id,
            'created_at': s.created_at,
            'symbol': s.symbol,
            'tf': s.tf,
            'signal': s.signal,
            'trend_score': features.get('trendScore', 0),
            'prob': features.get('prob', 0),
            'rsi': features.get('rsi', 50),
            'vol_mult': features.get('vol_mult', 1),
            'fwd_ret_10': labels.get(10).fwd_ret if 10 in labels else None,
            'broke_high': labels.get(10).broke_high if 10 in labels else None,
            'broke_low': labels.get(10).broke_low if 10 in labels else None,
        })
    
    db.close()
    return pd.DataFrame(data)


@st.cache_data(ttl=300)
def load_presets():
    """프리셋 로드"""
    manager = PresetManager()
    current = manager.load_preset(manager.current_preset_path)
    candidate = manager.load_preset(manager.candidate_preset_path)
    return current, candidate


@st.cache_data(ttl=300)
def load_experiments(limit: int = 10):
    """실험 결과 로드"""
    db = SessionLocal()
    experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()
    
    data = []
    for exp in experiments:
        metrics = exp.metrics
        data.append({
            'run_id': exp.run_id,
            'created_at': exp.created_at,
            'pf': metrics.get('pf', 0),
            'mdd': metrics.get('mdd', 0),
            'win_rate': metrics.get('win_rate', 0),
            'psu_10': metrics.get('psu_10', 0)
        })
    
    db.close()
    return pd.DataFrame(data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Plotly 다크 테마 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLOTLY_DARK_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        font=dict(color='#e6edf3', size=13, family='Segoe UI, Malgun Gothic'),
        xaxis=dict(gridcolor='#3b434d', linecolor='#30363d', color='#e6edf3'),
        yaxis=dict(gridcolor='#3b434d', linecolor='#30363d', color='#e6edf3'),
        title=dict(font=dict(size=18, color='#58a6ff', family='Segoe UI')),
        legend=dict(bgcolor='#161b22', bordercolor='#30363d', borderwidth=1)
    )
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 대시보드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tab1, tab2, tab3, tab4 = st.tabs(["신호 모니터링", "A/B 비교", "실험 히스토리", "프리셋 관리"])


# ═══════════════════════════════════════════════════════════
# 탭 1: 신호 모니터링
# ═══════════════════════════════════════════════════════════

with tab1:
    st.header("신호 모니터링")
    
    df_signals = load_signals(days_back, signal_filter, symbol_filter)
    
    if len(df_signals) == 0:
        st.warning("선택한 기간에 신호가 없습니다.")
    else:
        # ─── 통계 카드 ───
        st.subheader("전체 통계")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("총 신호", len(df_signals))
        
        with col2:
            buy_count = len(df_signals[df_signals['signal'] == 'BUY'])
            st.metric("BUY 신호", buy_count, 
                     delta=f"{buy_count/len(df_signals)*100:.0f}%" if len(df_signals) > 0 else "0%")
        
        with col3:
            sell_count = len(df_signals[df_signals['signal'] == 'SELL'])
            st.metric("SELL 신호", sell_count,
                     delta=f"{sell_count/len(df_signals)*100:.0f}%" if len(df_signals) > 0 else "0%")
        
        with col4:
            avg_prob = df_signals['prob'].mean()
            st.metric("평균 확률", f"{avg_prob:.2f}",
                     delta=f"{(avg_prob-0.5)*100:.0f}%" if avg_prob > 0 else "0%")
        
        with col5:
            avg_ts = df_signals['trend_score'].mean()
            st.metric("평균 TrendScore", f"{avg_ts:.0f}",
                     delta=f"{(avg_ts-50):.0f}" if avg_ts > 0 else "0")
        
        st.markdown("---")
        
        # ─── 시계열 차트 ───
        st.subheader("신호 발생 추이")
        
        df_timeline = df_signals.copy()
        df_timeline['date'] = pd.to_datetime(df_timeline['created_at']).dt.date
        timeline_counts = df_timeline.groupby(['date', 'signal']).size().reset_index(name='count')
        
        fig_timeline = px.bar(
            timeline_counts, x='date', y='count', color='signal',
            title="일별 신호 발생 빈도",
            color_discrete_map={'BUY': '#2ea043', 'SELL': '#f85149', 
                              'WATCH_UP': '#1f6feb', 'WATCH_DOWN': '#fb8500'},
            barmode='group', template=PLOTLY_DARK_TEMPLATE
        )
        fig_timeline.update_layout(height=400, xaxis_title="날짜", yaxis_title="신호 개수")
        st.plotly_chart(fig_timeline, width="stretch")
        
        # ─── 성과 분석 ───
        df_labeled = df_signals[df_signals['fwd_ret_10'].notna()]
        
        if len(df_labeled) > 0:
            st.markdown("---")
            st.subheader("신호 성과 분석 (10-bar forward)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### BUY 신호")
                df_buy = df_labeled[df_labeled['signal'] == 'BUY']
                
                if len(df_buy) > 0:
                    buy_metrics = PerformanceMetrics.calculate_all_metrics(df_buy, 'BUY')
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        st.metric("Profit Factor", f"{buy_metrics['pf']:.2f}")
                        st.metric("평균 수익률", f"{buy_metrics['avg_ret']*100:.2f}%")
                    with subcol2:
                        st.metric("승률", f"{buy_metrics['win_rate']*100:.1f}%")
                        st.metric("거래 횟수", f"{buy_metrics['total_trades']}")
                else:
                    st.info("데이터 없음")
            
            with col2:
                st.markdown("### SELL 신호")
                df_sell = df_labeled[df_labeled['signal'] == 'SELL']
                
                if len(df_sell) > 0:
                    sell_metrics = PerformanceMetrics.calculate_all_metrics(df_sell, 'SELL')
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        st.metric("Profit Factor", f"{sell_metrics['pf']:.2f}")
                        st.metric("평균 수익률", f"{sell_metrics['avg_ret']*100:.2f}%")
                    with subcol2:
                        st.metric("승률", f"{sell_metrics['win_rate']*100:.1f}%")
                        st.metric("거래 횟수", f"{sell_metrics['total_trades']}")
                else:
                    st.info("데이터 없음")
            
            with col3:
                st.markdown("### 전체 통계")
                all_ret = df_labeled['fwd_ret_10'].mean()
                all_win = (df_labeled['fwd_ret_10'] > 0).mean()
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    st.metric("전체 평균 수익률", f"{all_ret*100:.2f}%")
                    st.metric("고가 돌파율", f"{df_labeled['broke_high'].mean()*100:.0f}%")
                with subcol2:
                    st.metric("전체 승률", f"{all_win*100:.1f}%")
                    st.metric("저가 이탈율", f"{df_labeled['broke_low'].mean()*100:.0f}%")
            
            # ─── 수익률 분포 ───
            st.markdown("---")
            st.subheader("수익률 분포")
            
            fig_dist = px.histogram(
                df_labeled, x='fwd_ret_10', color='signal', nbins=30,
                title="10-bar Forward Return 분포",
                color_discrete_map={'BUY': '#2ea043', 'SELL': '#f85149'},
                marginal="box", template=PLOTLY_DARK_TEMPLATE
            )
            fig_dist.update_layout(height=400, xaxis_title="수익률", yaxis_title="빈도")
            st.plotly_chart(fig_dist, width="stretch")
        
        # ─── 최근 신호 테이블 & 상세 분석 ───
        st.markdown("---")
        st.subheader("최근 신호 목록")
        
        # 전체 신호 테이블 (먼저 표시)
        display_df = df_signals[[
            'created_at', 'symbol', 'tf', 'signal',
            'trend_score', 'prob', 'rsi', 'vol_mult', 'fwd_ret_10'
        ]].head(50).copy()
        
        display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['시각', '심볼', 'TF', '신호', 'TrendScore', 'Prob', 'RSI', 'VolMult', '10-bar 수익률']
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # 상세 분석 섹션
        st.markdown("---")
        st.subheader("신호 상세 분석 리포트")
        
        # 신호 선택
        signal_options = []
        for idx, row in df_signals.head(50).iterrows():
            created_at_str = pd.to_datetime(row['created_at']).strftime('%Y-%m-%d %H:%M')
            signal_label = f"{row['signal']} | {row['symbol']} ({row['tf']}) | {created_at_str}"
            signal_options.append((signal_label, row['id']))
        
        if signal_options:
            selected_label = st.selectbox(
                "신호를 선택하면 상세 애널리스트 리포트를 확인할 수 있습니다",
                [opt[0] for opt in signal_options],
                index=0
            )
            
            # 선택된 신호 ID 찾기
            selected_id = next((opt[1] for opt in signal_options if opt[0] == selected_label), None)
            
            if selected_id:
                # 선택된 신호 상세 정보 가져오기
                selected_signal = df_signals[df_signals['id'] == selected_id].iloc[0]
                
                # 데이터베이스에서 전체 정보 가져오기
                from signal_analyst import SignalAnalyst
                
                db = SessionLocal()
                signal_obj = db.query(Signal).filter(Signal.id == selected_id).first()
                
                if signal_obj:
                    # Signal 객체를 dict로 변환
                    signal_dict = {
                        'id': signal_obj.id,
                        'symbol': signal_obj.symbol,
                        'tf': signal_obj.tf,
                        'signal': signal_obj.signal,
                        'created_at': signal_obj.created_at,
                        'features_json': signal_obj.features_json
                    }
                    
                    # 애널리스트 리포트 생성
                    report = SignalAnalyst.generate_report(signal_dict)
                    
                    # 리포트 표시
                    st.markdown("---")
                    st.markdown(report)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="리포트 다운로드 (Markdown)",
                        data=report,
                        file_name=f"signal_report_{signal_obj.symbol}_{signal_obj.signal}_{pd.to_datetime(signal_obj.created_at).strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                db.close()


# ═══════════════════════════════════════════════════════════
# 탭 2: A/B 비교
# ═══════════════════════════════════════════════════════════

with tab2:
    st.header("프리셋 A/B 비교")
    
    try:
        current_preset, candidate_preset = load_presets()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Current Preset (A)")
            st.markdown(f"**버전:** `{current_preset.get('version', 'N/A')}`")
            
            if 'metrics' in current_preset:
                metrics = current_preset['metrics']
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Profit Factor", f"{metrics.get('pf', 0):.2f}")
                    st.metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%")
                with m2:
                    st.metric("Max Drawdown", f"{metrics.get('mdd', 0)*100:.2f}%")
                    st.metric("PSU Success", f"{metrics.get('psu_success', 0)*100:.1f}%")
            
            with st.expander("파라미터 상세보기"):
                st.json(current_preset.get('params', {}))
        
        with col2:
            st.subheader("Candidate Preset (B)")
            st.markdown(f"**버전:** `{candidate_preset.get('version', 'N/A')}`")
            
            if 'metrics' in candidate_preset:
                metrics = candidate_preset['metrics']
                m1, m2 = st.columns(2)
                with m1:
                    pf_diff = metrics.get('pf', 0) - current_preset.get('metrics', {}).get('pf', 0)
                    st.metric("Profit Factor", f"{metrics.get('pf', 0):.2f}", delta=f"{pf_diff:.2f}")
                    wr_diff = metrics.get('win_rate', 0) - current_preset.get('metrics', {}).get('win_rate', 0)
                    st.metric("Win Rate", f"{metrics.get('win_rate', 0)*100:.1f}%", delta=f"{wr_diff*100:.1f}%")
                with m2:
                    mdd_diff = metrics.get('mdd', 0) - current_preset.get('metrics', {}).get('mdd', 0)
                    st.metric("Max Drawdown", f"{metrics.get('mdd', 0)*100:.2f}%", 
                             delta=f"{mdd_diff*100:.2f}%", delta_color="inverse")
                    psu_diff = metrics.get('psu_success', 0) - current_preset.get('metrics', {}).get('psu_success', 0)
                    st.metric("PSU Success", f"{metrics.get('psu_success', 0)*100:.1f}%", delta=f"{psu_diff*100:.1f}%")
            
            with st.expander("파라미터 상세보기"):
                st.json(candidate_preset.get('params', {}))
        
        st.markdown("---")
        
        # 비교 차트
        st.subheader("성능 지표 비교")
        
        comparison_data = pd.DataFrame({
            'Metric': ['Profit Factor', 'Win Rate', 'MDD (inverted)'],
            'Current': [
                current_preset.get('metrics', {}).get('pf', 0),
                current_preset.get('metrics', {}).get('win_rate', 0),
                1 - current_preset.get('metrics', {}).get('mdd', 0)
            ],
            'Candidate': [
                candidate_preset.get('metrics', {}).get('pf', 0),
                candidate_preset.get('metrics', {}).get('win_rate', 0),
                1 - candidate_preset.get('metrics', {}).get('mdd', 0)
            ]
        })
        
        fig_comparison = go.Figure(data=[
            go.Bar(name='Current', x=comparison_data['Metric'], y=comparison_data['Current'], marker_color='#1f6feb'),
            go.Bar(name='Candidate', x=comparison_data['Metric'], y=comparison_data['Candidate'], marker_color='#f85149')
        ], layout=PLOTLY_DARK_TEMPLATE['layout'])
        
        fig_comparison.update_layout(barmode='group', title="프리셋 성능 비교", height=400)
        st.plotly_chart(fig_comparison, width="stretch")
        
        # 승격 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Candidate를 Current로 승격", use_container_width=True, type="primary"):
                manager = PresetManager()
                if manager.promote_candidate_to_current():
                    st.success("Candidate가 Current로 승격되었습니다!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("승격 실패")
        
    except Exception as e:
        st.error(f"프리셋 로드 실패: {e}")


# ═══════════════════════════════════════════════════════════
# 탭 3: 실험 히스토리
# ═══════════════════════════════════════════════════════════

with tab3:
    st.header("실험 히스토리")
    
    df_experiments = load_experiments(20)
    
    if len(df_experiments) == 0:
        st.info("실험 기록이 없습니다. Learner를 실행하세요.")
    else:
        st.subheader("최근 실험 결과")
        
        display_exp = df_experiments.copy()
        display_exp['created_at'] = pd.to_datetime(display_exp['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        display_exp.columns = ['Run ID', '생성 시각', 'Profit Factor', 'Max Drawdown', 'Win Rate', 'PSU 10-bar']
        
        st.dataframe(display_exp, width="stretch", height=400)
        
        st.markdown("---")
        st.subheader("실험 성능 추이")
        
        fig_exp = make_subplots(rows=2, cols=2, subplot_titles=("Profit Factor", "Max Drawdown", "Win Rate", "PSU 10-bar"))
        
        fig_exp.add_trace(go.Scatter(x=df_experiments.index, y=df_experiments['pf'], 
                                     mode='lines+markers', name='PF', line=dict(color='#1f6feb', width=3)), row=1, col=1)
        fig_exp.add_trace(go.Scatter(x=df_experiments.index, y=df_experiments['mdd'],
                                     mode='lines+markers', name='MDD', line=dict(color='#f85149', width=3)), row=1, col=2)
        fig_exp.add_trace(go.Scatter(x=df_experiments.index, y=df_experiments['win_rate'],
                                     mode='lines+markers', name='WR', line=dict(color='#2ea043', width=3)), row=2, col=1)
        fig_exp.add_trace(go.Scatter(x=df_experiments.index, y=df_experiments['psu_10'],
                                     mode='lines+markers', name='PSU', line=dict(color='#fb8500', width=3)), row=2, col=2)
        
        fig_exp.update_layout(height=600, showlegend=False, **PLOTLY_DARK_TEMPLATE['layout'])
        st.plotly_chart(fig_exp, width="stretch")


# ═══════════════════════════════════════════════════════════
# 탭 4: 프리셋 관리
# ═══════════════════════════════════════════════════════════

with tab4:
    st.header("프리셋 관리")
    
    try:
        current_preset, candidate_preset = load_presets()
        manager = PresetManager()
        
        st.subheader("Pine Script 파라미터 (복사용)")
        
        preset_choice = st.radio("프리셋 선택", ["Current", "Candidate"], horizontal=True)
        
        selected_preset = current_preset if preset_choice == "Current" else candidate_preset
        pine_code = manager.generate_pine_script_comment(selected_preset)
        
        st.code(pine_code, language="javascript")
        
        st.markdown('<div class="info-box">위 코드를 복사하여 TradingView Pine Script 지표에 붙여넣으세요.</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"프리셋 로드 실패: {e}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 푸터
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8b949e; padding: 2rem 0;'>
    <p style='font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; color: #58a6ff;'>
        VMSI-SDM v3.0 | 자가학습형 TradingView 지표 시스템
    </p>
    <p style='font-size: 0.9rem;'>
        문의: docs/README.md 참조 | 포트: 8501 (Dashboard) / 8000 (API Server)
    </p>
</div>
""", unsafe_allow_html=True)
