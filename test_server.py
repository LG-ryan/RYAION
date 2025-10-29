"""서버 상태 확인 스크립트"""
import requests
import time

print("서버 상태 확인 중...")
time.sleep(3)  # 서버 시작 대기

try:
    response = requests.get("http://localhost:8000/", timeout=5)
    if response.status_code == 200:
        print("\n" + "="*60)
        print("✅ 서버가 정상적으로 실행 중입니다!")
        print("="*60)
        print(f"\n서버 응답: {response.json()}")
        print("\n📍 접속 주소:")
        print("   - API: http://localhost:8000")
        print("   - 문서: http://localhost:8000/docs")
        print("\n" + "="*60)
    else:
        print(f"⚠️  서버 응답 코드: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("\n" + "="*60)
    print("❌ 서버에 연결할 수 없습니다.")
    print("="*60)
    print("\n서버가 아직 시작 중이거나 오류가 발생했을 수 있습니다.")
    print("\n수동 실행 방법:")
    print("   python server\\app.py")
except Exception as e:
    print(f"\n오류 발생: {e}")


