# 🚀 VMSI-SDM 클라우드 배포 체크리스트

## ✅ Phase 1: GitHub 저장소 준비 (5분)

### 1-1. Git 초기화
```powershell
cd C:\Users\ryanj\RYAION\vmsi-sdm

# Git 초기화 (이미 완료되었다면 skip)
git init
git add .
git commit -m "Initial commit: VMSI-SDM v2.1 with cloud deployment config"
```

### 1-2. GitHub 저장소 생성 및 푸시
```
1. https://github.com 접속
2. 로그인
3. "New repository" 클릭
4. Repository name: vmsi-sdm
5. Public 또는 Private 선택
6. "Create repository" (README, .gitignore 추가하지 말 것!)
```

```powershell
# 원격 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/vmsi-sdm.git
git branch -M main
git push -u origin main
```

---

## ✅ Phase 2: Render 배포 (10분)

### 2-1. Render 계정 생성
```
1. https://render.com 접속
2. "Get Started for Free" 클릭
3. GitHub 계정으로 로그인
4. Render가 GitHub 저장소 접근 권한 승인
```

### 2-2. PostgreSQL 데이터베이스 생성
```
1. Render Dashboard → "New +" → "PostgreSQL"
2. 설정:
   Name: vmsi-sdm-db
   Database: vmsi_sdm
   User: vmsi_sdm_user
   Region: Oregon (Free)
   Plan: Free
3. "Create Database" 클릭
4. 생성 완료 후 "Internal Database URL" 복사
   형식: postgresql://vmsi_sdm_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/vmsi_sdm
```

### 2-3. Web Service 생성
```
1. Render Dashboard → "New +" → "Web Service"
2. "Connect a repository" → vmsi-sdm 선택
3. 설정:
   Name: vmsi-sdm-api
   Region: Oregon (Free)
   Branch: main
   Root Directory: (비워둠)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn server.app:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
4. "Environment Variables" 섹션:
   Key: DATABASE_URL
   Value: (위에서 복사한 PostgreSQL URL)
5. "Create Web Service" 클릭
```

### 2-4. 배포 확인 (5-10분 소요)
```
1. 로그 화면에서 배포 진행 상황 확인
2. "Your service is live" 메시지 대기
3. URL 복사 (예: https://vmsi-sdm-api.onrender.com)
4. 브라우저에서 접속하여 헬스 체크:
   https://vmsi-sdm-api.onrender.com/
   → {"status": "ok", "message": "..."} 응답 확인
```

### 2-5. 데이터베이스 초기화
```powershell
# 로컬에서 Render DB에 연결하여 초기화
cd C:\Users\ryanj\RYAION\vmsi-sdm

# 환경변수 설정
$env:DATABASE_URL="postgresql://vmsi_sdm_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/vmsi_sdm"

# DB 초기화
python server/db.py
```

---

## ✅ Phase 3: Streamlit Cloud 배포 (5분)

### 3-1. Streamlit Cloud 가입
```
1. https://streamlit.io/cloud 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인
```

### 3-2. 앱 배포
```
1. "New app" 클릭
2. 설정:
   Repository: YOUR_USERNAME/vmsi-sdm
   Branch: main
   Main file path: dashboard/app.py
3. "Advanced settings" 클릭
4. "Secrets" 탭:
   DATABASE_URL = "postgresql://vmsi_sdm_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/vmsi_sdm"
5. "Deploy!" 클릭
```

### 3-3. 배포 확인
```
1. 로그 화면에서 배포 진행 상황 확인 (2-5분)
2. 배포 완료 후 자동으로 앱 열림
3. URL 확인 (예: https://YOUR_USERNAME-vmsi-sdm.streamlit.app)
```

---

## ✅ Phase 4: GitHub Actions 설정 (3분)

### 4-1. GitHub Secrets 설정
```
1. GitHub 저장소 페이지 접속
   https://github.com/YOUR_USERNAME/vmsi-sdm
2. Settings → Secrets and variables → Actions
3. "New repository secret" 클릭
4. 두 개의 Secret 추가:

   Secret 1:
   Name: DATABASE_URL
   Secret: postgresql://vmsi_sdm_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/vmsi_sdm

   Secret 2:
   Name: RENDER_URL
   Secret: https://vmsi-sdm-api.onrender.com

5. "Add secret" 클릭
```

### 4-2. Workflow 수동 실행 테스트
```
1. GitHub 저장소 → Actions 탭
2. "Optuna Learning Loop" 선택
3. "Run workflow" → "Run workflow" 클릭
4. 실행 로그 확인 (초반에는 데이터 없어서 실패 가능 - 정상)
```

---

## ✅ Phase 5: TradingView 연결 (2분)

### 5-1. Indicator 추가
```
1. TradingView Pine Editor 열기
2. C:\Users\ryanj\RYAION\vmsi-sdm\pine\indicator_sdm_v2.pine 파일 열기
3. 전체 복사 (Ctrl+A → Ctrl+C)
4. Pine Editor에 붙여넣기 (Ctrl+V)
5. "Save" → "Add to Chart"
```

### 5-2. Alert 생성
```
1. 차트 우측 상단 "알림 생성" (시계 아이콘) 클릭
2. 설정:
   조건: "VMSI-SDM v2"
   조건 선택: "어떤 alert() 함수 호출"
   만료: "차트와 같게"
   만료일: 원하는 날짜
3. "Webhook URL" 체크박스 활성화
4. URL 입력:
   https://vmsi-sdm-api.onrender.com/alert
5. "만들기" 클릭
```

---

## ✅ Phase 6: 최종 확인 (5분)

### 6-1. 시스템 상태 확인
```
□ Render FastAPI 서버: https://vmsi-sdm-api.onrender.com/
  → {"status": "ok"} 응답
  
□ Streamlit 대시보드: https://YOUR_USERNAME-vmsi-sdm.streamlit.app
  → 대시보드 정상 표시
  
□ GitHub Actions: https://github.com/YOUR_USERNAME/vmsi-sdm/actions
  → Workflow 파일 존재 확인
  
□ TradingView Alert: 차트에서 알림 아이콘 확인
  → Webhook URL 설정 확인
```

### 6-2. 수동 테스트 (선택사항)
```powershell
# 로컬에서 Webhook 테스트
cd C:\Users\ryanj\RYAION\vmsi-sdm

$body = Get-Content test_alert.json -Raw
Invoke-RestMethod -Uri "https://vmsi-sdm-api.onrender.com/alert" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

```
1. Streamlit 대시보드 새로고침
2. "최근 신호 목록" 탭 확인
3. 새 신호 표시 확인
```

---

## 🎯 완료!

### 시스템 구성
```
✅ Render FastAPI 서버 (24/7 가동)
   → TradingView Webhook 수신
   
✅ Render PostgreSQL (무료 1GB)
   → 신호 및 라벨 저장
   
✅ Streamlit Cloud (무료 무제한)
   → 대시보드 시각화
   
✅ GitHub Actions (매일 오전 2시 UTC)
   → 자동 학습 루프
   
✅ TradingView Alert
   → 실시간 신호 전송
```

### 비용
```
총 비용: $0 / 월 (완전 무료!)
```

### 주의사항
```
⚠️ Render 무료 플랜: 15분 비활성 시 sleep
   → Keep Alive workflow가 5분마다 ping (자동)
   
⚠️ 첫 요청 시 ~30초 재시작 시간
   → Keep Alive로 최소화
   
⚠️ PostgreSQL: 1GB 제한
   → 약 3년치 데이터 저장 가능
```

---

## 🆘 문제 해결

### Render 배포 실패
```
1. Render Dashboard → 해당 서비스 → "Logs" 확인
2. requirements.txt 확인
3. 환경변수 (DATABASE_URL) 확인
4. Start Command 확인
```

### Streamlit 배포 실패
```
1. Streamlit Cloud → 해당 앱 → "Logs" 확인
2. requirements_streamlit.txt 확인 (파일 이름 주의!)
3. Main file path 확인: dashboard/app.py
4. Secrets의 DATABASE_URL 확인
```

### TradingView Webhook 실패
```
1. Render 서버가 sleep 상태인지 확인
   → https://vmsi-sdm-api.onrender.com/ 접속하여 깨우기
2. Alert URL 확인 (/alert 경로 포함)
3. Indicator가 차트에 추가되어 있는지 확인
4. Alert 조건: "어떤 alert() 함수 호출" 선택 확인
```

### GitHub Actions 실패
```
1. Actions 탭에서 로그 확인
2. Secrets (DATABASE_URL, RENDER_URL) 설정 확인
3. 데이터 부족 오류: 정상 (신호 수집 후 재실행)
```

---

## 📊 다음 단계

1. **실시간 신호 대기**
   - TradingView에서 BUY/SELL 신호 발생 시 자동 수집
   
2. **대시보드 모니터링**
   - Streamlit Cloud에서 신호 확인
   
3. **자동 학습 대기**
   - 매일 오전 2시 UTC (한국 11시)에 자동 실행
   - 또는 GitHub Actions에서 수동 실행
   
4. **성능 비교**
   - preset_A vs preset_B 백테스트
   - 더 나은 파라미터 선택

---

**🎉 24/7 자동화 시스템 구축 완료!**
**PC 없이도 계속 작동합니다!**

