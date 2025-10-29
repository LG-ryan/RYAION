#!/bin/bash
# VMSI-SDM Linux/Mac 초기화 스크립트

echo "============================================================"
echo "🚀 VMSI-SDM 프로젝트 초기화"
echo "============================================================"
echo ""

# Python 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3이 설치되어 있지 않습니다."
    echo "   Python 3.9 이상을 설치하세요."
    exit 1
fi

echo "✓ Python 확인 완료"
python3 --version

echo ""
echo "[1/5] 가상환경 생성 중..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패"
    exit 1
fi
echo "✓ 가상환경 생성 완료"

echo ""
echo "[2/5] 가상환경 활성화 중..."
source venv/bin/activate
echo "✓ 가상환경 활성화 완료"

echo ""
echo "[3/5] 패키지 설치 중..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치 실패"
    exit 1
fi
echo "✓ 패키지 설치 완료"

echo ""
echo "[4/5] 환경변수 파일 생성 중..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "✓ .env 파일 생성 완료"
else
    echo "✓ .env 파일 이미 존재"
fi

echo ""
echo "[5/5] 데이터베이스 초기화 중..."
python -c "from server.db import init_db; init_db()"
if [ $? -ne 0 ]; then
    echo "❌ 데이터베이스 초기화 실패"
    exit 1
fi
echo "✓ 데이터베이스 초기화 완료"

echo ""
echo "============================================================"
echo "🎉 초기화 완료!"
echo "============================================================"
echo ""
echo "📋 다음 단계:"
echo ""
echo "  1. 서버 실행:"
echo "     python server/app.py"
echo ""
echo "  2. 대시보드 실행 (새 터미널):"
echo "     streamlit run dashboard/app.py"
echo ""
echo "  3. TradingView 연결:"
echo "     pine/indicator_sdm_v2.pine 복사 후 TradingView에 추가"
echo ""
echo "  자세한 내용: QUICKSTART.md 참조"
echo ""
echo "============================================================"


