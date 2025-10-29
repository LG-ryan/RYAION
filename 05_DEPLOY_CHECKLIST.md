# ✅ 배포 체크리스트 (로컬 ngrok 환경)

**환경**: ngrok + 로컬 PC (100% 무료)

---

## 📋 초기 설정 (최초 1회)

### 1. Python 환경
```bash
- [ ] Python 3.10+ 설치
- [ ] pip 최신 버전
- [ ] 패키지 설치: pip install -r requirements.txt
```

### 2. ngrok 설정
```bash
- [ ] ngrok 다운로드 (https://ngrok.com/)
- [ ] ngrok.exe를 vmsi-sdm 폴더에 복사
- [ ] Authtoken 설정: .\ngrok.exe config add-authtoken YOUR_TOKEN
```

### 3. 데이터베이스 초기화
```bash
- [ ] SQLite 자동 생성 확인 (vmsi_sdm.db)
- [ ] 테이블 생성 확인: python -c "from server.db import init_db; init_db()"
```

### 4. Pine Script 업로드
```bash
- [ ] TradingView에 indicator_sdm_v2.pine 추가
- [ ] (선택) strategy_sdm_v2.pine 백테스트
```

---

## 🚀 일일 시작 루틴

### 트레이딩 시작 시
```bash
1. [ ] start_all.bat 실행
   - FastAPI 서버 (port 8000)
   - ngrok 터널
   - Streamlit 대시보드 (port 8501)

2. [ ] ngrok URL 확인
   - 브라우저: http://localhost:4040
   - 또는: check_ngrok_url.bat 실행
   - Public URL 복사: https://abc123.ngrok-free.app

3. [ ] TradingView Alert 설정/업데이트
   - Webhook URL: https://abc123.ngrok-free.app/webhook/tv
   - Condition: alert() function calls only
   - Once Per Bar Close 체크
```

---

## 🔄 2시간마다 (ngrok 세션 만료 시)

```bash
1. [ ] ngrok 터미널에서 Ctrl+C (종료)
2. [ ] start_ngrok.bat 재실행
3. [ ] 새 URL 확인 (http://localhost:4040)
4. [ ] TradingView Alert Webhook URL 업데이트
```

**소요 시간**: 30초

---

## 📊 모니터링

### 실시간 확인
```bash
- [ ] FastAPI Health: http://localhost:8000/health
- [ ] Streamlit 대시보드: http://localhost:8501
- [ ] ngrok Web Interface: http://localhost:4040
```

### 신호 확인
```bash
- [ ] Streamlit → "최근 신호 목록"
- [ ] 수동 테스트: Test 3 (Webhook 신호 전송)
```

---

## 🤖 자동 학습 설정 (선택)

### Windows Task Scheduler
```bash
1. [ ] 작업 스케줄러 열기
2. [ ] 작업 만들기: "VMSI-SDM Optuna Learning"
3. [ ] 트리거: 매일 오전 2:00
4. [ ] 동작: run_learning.bat 실행
5. [ ] 조건: AC 전원 체크 해제
```

---

## 🔧 트러블슈팅

### FastAPI 시작 안 됨
```bash
- [ ] Port 8000 확인: taskkill /f /im uvicorn.exe
- [ ] 재시작: start_server.bat
```

### ngrok 연결 안 됨
```bash
- [ ] Authtoken 확인
- [ ] 인터넷 연결 확인
- [ ] ngrok 재시작
```

### SQLite 오류
```bash
- [ ] 모든 프로그램 종료
- [ ] vmsi_sdm.db 삭제
- [ ] python -c "from server.db import init_db; init_db()"
```

---

## 📝 주요 파일

```
vmsi-sdm/
├── start_all.bat          ← 통합 시작 (FastAPI + ngrok + Streamlit)
├── start_ngrok.bat        ← ngrok만 시작
├── check_ngrok_url.bat    ← ngrok URL 확인
├── run_learning.bat       ← 수동 학습 실행
├── vmsi_sdm.db           ← SQLite 데이터베이스
├── ngrok.exe             ← ngrok 실행 파일
├── server/               ← FastAPI 서버
├── dashboard/            ← Streamlit 대시보드
├── learner/              ← Optuna 학습
└── pine/                 ← TradingView Pine Scripts
```

---

## 🎯 완료 확인

### 시스템 정상 작동 체크리스트
```bash
- [ ] FastAPI 응답: http://localhost:8000/health → {"status":"healthy"}
- [ ] ngrok 터널 활성: http://localhost:4040 → Public URL 확인
- [ ] Streamlit 표시: http://localhost:8501 → 대시보드 로딩
- [ ] Webhook 테스트: Test 3 성공 → 신호 저장 확인
- [ ] TradingView Alert: Webhook URL 설정 완료
```

---

## 💡 Pro Tips

### 비용 절감
```
✅ ngrok Free: $0/월 (2시간 세션)
✅ ngrok Paid: $10/월 (고정 URL, 무제한)
```

### 성능 최적화
```
✅ 로컬 PC: 클라우드보다 빠름
✅ 무제한 학습: run_learning.bat → trials 500+
✅ SQLite: 빠른 속도, 직접 제어
```

### 백업
```
✅ 정기적 백업: vmsi_sdm.db, presets/*.json
✅ GitHub: 코드 버전 관리
```

---

**작성**: Cursor AI  
**날짜**: 2025-10-29  
**환경**: ngrok + 로컬 PC (100% 무료)

🏠 **로컬 최고! PC에서 모든 것을!**
