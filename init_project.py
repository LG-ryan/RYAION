"""
VMSI-SDM 프로젝트 초기화 스크립트
데이터베이스 초기화 및 기본 설정
"""

import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from server.db import init_db, SessionLocal
from learner.preset import PresetManager


def main():
    """프로젝트 초기화 메인 함수"""
    
    print("=" * 60)
    print("🚀 VMSI-SDM 프로젝트 초기화 시작...")
    print("=" * 60)
    print()
    
    # 1. 데이터베이스 초기화
    print("📦 [1/4] 데이터베이스 초기화 중...")
    try:
        init_db()
        print("   ✓ 데이터베이스 초기화 완료 (SQLite)")
    except Exception as e:
        print(f"   ❌ 데이터베이스 초기화 실패: {e}")
        return False
    
    # 2. 기본 프리셋 생성
    print("\n🎨 [2/4] 기본 프리셋 생성 중...")
    try:
        manager = PresetManager()
        default_preset = manager._get_default_preset()
        manager.save_preset(default_preset, manager.current_preset_path)
        print("   ✓ preset_A_current.json 생성 완료")
        
        # Candidate 프리셋도 확인
        if not manager.candidate_preset_path.exists():
            manager.save_preset(default_preset, manager.candidate_preset_path)
            print("   ✓ preset_B_candidate.json 생성 완료")
        else:
            print("   ✓ preset_B_candidate.json 이미 존재")
    except Exception as e:
        print(f"   ❌ 프리셋 생성 실패: {e}")
        return False
    
    # 3. 디렉토리 구조 확인
    print("\n📁 [3/4] 디렉토리 구조 확인 중...")
    required_dirs = ['pine', 'server', 'learner', 'dashboard', 'presets', 'docs']
    all_exist = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   ✓ {dir_name}/ 존재")
        else:
            print(f"   ❌ {dir_name}/ 없음")
            all_exist = False
    
    if not all_exist:
        print("   ⚠️  일부 디렉토리가 없습니다.")
    
    # 4. 모듈 임포트 테스트
    print("\n🔧 [4/4] 모듈 임포트 테스트 중...")
    modules_ok = True
    
    try:
        from server.app import app
        print("   ✓ server.app")
    except Exception as e:
        print(f"   ❌ server.app: {e}")
        modules_ok = False
    
    try:
        from learner.tune import ParameterTuner
        print("   ✓ learner.tune")
    except Exception as e:
        print(f"   ❌ learner.tune: {e}")
        modules_ok = False
    
    try:
        from dashboard.app import st
        print("   ✓ dashboard.app")
    except Exception as e:
        print(f"   ❌ dashboard.app: {e}")
        modules_ok = False
    
    # 최종 결과
    print()
    print("=" * 60)
    if modules_ok and all_exist:
        print("🚀 프로젝트 초기화 완료: VMSI-SDM")
        print("=" * 60)
        print()
        print("✅ 모듈:")
        print("   ✓ server   - FastAPI Webhook 서버")
        print("   ✓ learner  - Optuna 학습 엔진")
        print("   ✓ dashboard - Streamlit 대시보드")
        print("   ✓ pine     - TradingView Pine Script")
        print()
        print("📚 다음 단계:")
        print("   1. 서버 실행:")
        print("      python server/app.py")
        print("      또는")
        print("      uvicorn server.app:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("   2. 대시보드 실행:")
        print("      streamlit run dashboard/app.py")
        print()
        print("   3. TradingView 연결:")
        print("      - pine/indicator_sdm_v2.pine을 TradingView에 추가")
        print("      - Alert Webhook URL: http://your-ip:8000/alert")
        print()
        print("   4. 테스트:")
        print("      curl -X POST http://localhost:8000/alert -H 'Content-Type: application/json' -d @test_alert.json")
        print()
        print("=" * 60)
        print("📖 문서: docs/README.md")
        print("🔗 API 문서: http://localhost:8000/docs (서버 실행 후)")
        print("=" * 60)
        return True
    else:
        print("❌ 초기화 중 오류 발생")
        print("=" * 60)
        print()
        print("🔍 문제 해결:")
        print("   1. 패키지 설치: pip install -r requirements.txt")
        print("   2. 경로 확인: 프로젝트 루트에서 실행하세요")
        print("   3. Python 버전: Python 3.9+ 필요")
        print()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


