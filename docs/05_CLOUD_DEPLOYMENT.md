# 🌐 무료 클라우드 배포 가이드 (PC 없이 24/7 자동화)

## 🎯 목표

PC가 꺼져있어도 자동으로 작동하는 VMSI-SDM 시스템 구축 (100% 무료)

---

## 📊 아키텍처 설계

### 최종 구조
```
TradingView (미국)
    ↓ Webhook
Render (FastAPI 서버) ← 무료 750시간/월
    ↓ 데이터 저장
PostgreSQL (Render) ← 무료
    ↓ 데이터 읽기
Streamlit Cloud (대시보드) ← 무료 무제한
    
GitHub Actions (학습 루프) ← 무료 2000분/월
    ↓ 최적 파라미터 저장
PostgreSQL (Render)
```

---

## 🆓 무료 서비스 조합

| 서비스 | 용도 | 무료 플랜 | 제한 |
|--------|------|-----------|------|
| **Render** | FastAPI 서버 + DB | 750시간/월 | 15분 비활성 시 sleep |
| **Streamlit Cloud** | 대시보드 | 무제한 | 1개 앱 |
| **GitHub Actions** | 자동 학습 | 2000분/월 | 충분함 |
| **Railway** | 대안 (올인원) | $5 크레딧/월 | 월말 중단 가능 |

### 권장: **Render + Streamlit Cloud + GitHub Actions**
- 완전 무료
- 설정 간단
- 안정적

---

## 📦 배포 순서

### Phase 1: Render (FastAPI 서버) 배포
### Phase 2: PostgreSQL 설정
### Phase 3: Streamlit Cloud 배포
### Phase 4: GitHub Actions 학습 자동화
### Phase 5: TradingView 연결

---

# Phase 1: Render 배포 (FastAPI 서버)

## Step 1-1: 프로젝트 준비

### 1. requirements.txt 확인
```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
pydantic==2.9.2
python-dotenv==1.0.1
pandas==2.2.3
numpy==2.1.2
scikit-learn==1.5.2
optuna==4.0.0
yfinance==0.2.48
alembic==1.13.3
```

### 2. `Procfile` 생성 (Render용)
```bash
# vmsi-sdm/Procfile
web: uvicorn server.app:app --host 0.0.0.0 --port $PORT
```

### 3. `render.yaml` 생성 (선택사항, 자동 설정)
```yaml
# vmsi-sdm/render.yaml
services:
  - type: web
    name: vmsi-sdm-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: vmsi-sdm-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.11.0

databases:
  - name: vmsi-sdm-db
    plan: free
    databaseName: vmsi_sdm
    user: vmsi_sdm_user
```

### 4. 환경변수 파일 업데이트
```python
# vmsi-sdm/.env.example
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
```

---

## Step 1-2: GitHub 저장소 생성

### 1. GitHub 계정 생성 (무료)
```
https://github.com/signup
```

### 2. 로컬에서 Git 초기화
```powershell
cd C:\Users\ryanj\RYAION\vmsi-sdm

# Git 초기화
git init

# .gitignore 생성 (중요!)
echo "# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temp
*.tmp
temp/
" > .gitignore

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: VMSI-SDM v2.1"
```

### 3. GitHub에 푸시
```powershell
# GitHub에서 새 레포지토리 생성 (vmsi-sdm)
# 그 다음:

git remote add origin https://github.com/YOUR_USERNAME/vmsi-sdm.git
git branch -M main
git push -u origin main
```

---

## Step 1-3: Render 배포

### 1. Render 계정 생성
```
https://render.com/
→ "Sign Up" → GitHub 연동
```

### 2. PostgreSQL 데이터베이스 생성
```
1. Render Dashboard → "New +"
2. "PostgreSQL" 선택
3. 설정:
   - Name: vmsi-sdm-db
   - Database: vmsi_sdm
   - User: vmsi_sdm_user
   - Region: Oregon (Free)
   - Plan: Free
4. "Create Database"

5. 생성 후 "Internal Database URL" 복사
   예: postgresql://vmsi_sdm_user:xxxx@dpg-xxxx-oregon-postgres.render.com/vmsi_sdm
```

### 3. Web Service 생성
```
1. Render Dashboard → "New +"
2. "Web Service" 선택
3. GitHub 저장소 연결:
   - "Connect Repository"
   - "vmsi-sdm" 선택
4. 설정:
   - Name: vmsi-sdm-api
   - Region: Oregon (Free)
   - Branch: main
   - Root Directory: (비워둠)
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn server.app:app --host 0.0.0.0 --port $PORT
   - Plan: Free
5. "Environment Variables" 추가:
   - DATABASE_URL: (위에서 복사한 PostgreSQL URL)
   - ENVIRONMENT: production
6. "Create Web Service"
```

### 4. 배포 확인
```
1. 배포 로그 확인 (5-10분 소요)
2. 배포 완료 후 URL 확인:
   예: https://vmsi-sdm-api.onrender.com

3. 헬스 체크:
   브라우저에서 접속:
   https://vmsi-sdm-api.onrender.com/
   
   → {"status": "ok", "message": "VMSI-SDM API Server"} 출력
```

---

## Step 1-4: 데이터베이스 초기화

### 로컬에서 Render DB에 연결
```powershell
cd C:\Users\ryanj\RYAION\vmsi-sdm

# 환경변수 설정
$env:DATABASE_URL="postgresql://vmsi_sdm_user:xxxx@dpg-xxxx-oregon-postgres.render.com/vmsi_sdm"

# DB 초기화
python server/db.py
```

---

# Phase 2: Streamlit Cloud 배포 (대시보드)

## Step 2-1: Streamlit 앱 준비

### 1. `requirements_streamlit.txt` 생성
```txt
streamlit==1.39.0
pandas==2.2.3
plotly==5.24.1
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
```

### 2. Streamlit 설정 파일
```toml
# vmsi-sdm/.streamlit/config.toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#161b22"
textColor = "#e6edf3"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true
```

---

## Step 2-2: Streamlit Cloud 배포

### 1. Streamlit Cloud 가입
```
https://streamlit.io/cloud
→ "Sign up" → GitHub 연동
```

### 2. 앱 배포
```
1. "New app" 클릭
2. 설정:
   - Repository: YOUR_USERNAME/vmsi-sdm
   - Branch: main
   - Main file path: dashboard/app.py
3. "Advanced settings" → Environment variables:
   - DATABASE_URL: (Render PostgreSQL URL)
4. "Deploy!"
```

### 3. 배포 확인
```
URL: https://YOUR_USERNAME-vmsi-sdm.streamlit.app
→ 대시보드 접속 확인
```

---

# Phase 3: GitHub Actions (자동 학습)

## Step 3-1: Workflow 파일 생성

### `.github/workflows/optuna_learning.yml`
```yaml
name: Optuna Learning Loop

on:
  schedule:
    # 매일 오전 2시 (한국 시간 11시)
    - cron: '0 2 * * *'
  workflow_dispatch: # 수동 실행 가능

jobs:
  learn:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run Optuna learning
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
      run: |
        python learner/tune.py --trials 50 --timeout 3600
    
    - name: Upload results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: learning-results
        path: |
          presets/preset_B_candidate.json
          learner/optuna_study.db
```

---

## Step 3-2: GitHub Secrets 설정

```
1. GitHub 저장소 → Settings
2. Secrets and variables → Actions
3. "New repository secret":
   - Name: DATABASE_URL
   - Secret: (Render PostgreSQL URL)
4. "Add secret"
```

---

## Step 3-3: 학습 스크립트 수정

### `learner/tune.py` 업데이트 (클라우드용)
```python
# learner/tune.py
import os
import argparse
from sqlalchemy import create_engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=50)
    parser.add_argument('--timeout', type=int, default=3600)
    args = parser.parse_args()
    
    # 환경변수에서 DB URL 가져오기
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not set")
        exit(1)
    
    print(f"[INFO] Starting Optuna with {args.trials} trials, {args.timeout}s timeout")
    
    # ... 기존 학습 로직 ...
    
    print("[OK] Learning completed!")

if __name__ == "__main__":
    main()
```

---

# Phase 4: TradingView 연결

## Step 4-1: Render URL로 Webhook 설정

### 1. Render 서버 URL 확인
```
예: https://vmsi-sdm-api.onrender.com
```

### 2. TradingView Alert 설정
```
1. Indicator 추가 (indicator_sdm_v2.pine)
2. "알림 생성" 클릭
3. 조건: "VMSI-SDM v2"
4. "어떤 alert() 함수 호출"
5. Webhook URL:
   https://vmsi-sdm-api.onrender.com/alert
6. "만들기"
```

### ✅ ngrok 불필요!
```
Render가 공인 URL 제공 → TradingView가 바로 접속 가능
PC 켜져 있지 않아도 작동!
```

---

# 🚀 전체 시스템 흐름

## 1. 실시간 신호 수신 (24/7)
```
TradingView 신호 발생
    ↓
Render FastAPI 서버 (항상 켜짐)
    ↓
PostgreSQL에 저장
    ↓
Streamlit Cloud 대시보드에서 확인 가능
```

## 2. 자동 학습 (매일 오전 2시)
```
GitHub Actions 스케줄러 트리거
    ↓
Optuna 학습 실행 (50회 시도, 1시간)
    ↓
최적 파라미터 → preset_B_candidate.json
    ↓
PostgreSQL에 실험 결과 저장
    ↓
Streamlit 대시보드에서 A/B 비교
```

## 3. 수동 백테스트 (필요 시)
```
TradingView Strategy로 백테스트
    ↓
preset_A vs preset_B 성능 비교
    ↓
더 나은 파라미터 선택
```

---

# ⚠️ 주의사항

## 1. Render Free Tier 제한
```
- 15분 비활성 시 sleep 모드
- 첫 요청 시 ~30초 재시작 시간
- 해결: Cron job으로 5분마다 health check 요청
```

### Health Check Workflow 추가
```yaml
# .github/workflows/keep_alive.yml
name: Keep Render Alive

on:
  schedule:
    # 5분마다 실행
    - cron: '*/5 * * * *'

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
    - name: Ping server
      run: |
        curl https://vmsi-sdm-api.onrender.com/
```

## 2. PostgreSQL 용량
```
- 무료: 1GB
- 신호 저장: ~1MB/일
- 약 3년치 데이터 저장 가능
- 오래된 데이터 정리 스크립트 추가 권장
```

## 3. GitHub Actions 시간 제한
```
- 무료: 2000분/월
- 매일 1시간 학습: ~30시간/월
- 충분함! (66% 여유)
```

---

# 📊 비용 분석

| 항목 | 비용 | 월간 |
|------|------|------|
| Render Web Service | 무료 | $0 |
| Render PostgreSQL | 무료 | $0 |
| Streamlit Cloud | 무료 | $0 |
| GitHub Actions | 무료 | $0 |
| **총계** | **$0** | **$0** |

---

# 🎯 배포 체크리스트

## Phase 1: Render
```
□ GitHub 저장소 생성
□ Git 초기화 및 푸시
□ Render 계정 생성
□ PostgreSQL 데이터베이스 생성
□ Web Service 배포
□ 환경변수 설정 (DATABASE_URL)
□ 헬스 체크 확인
□ DB 초기화 완료
```

## Phase 2: Streamlit Cloud
```
□ Streamlit Cloud 가입
□ 앱 배포
□ 환경변수 설정
□ 대시보드 접속 확인
```

## Phase 3: GitHub Actions
```
□ Workflow 파일 생성 (.github/workflows/)
□ Secrets 설정 (DATABASE_URL)
□ 학습 스크립트 수정
□ Keep Alive workflow 추가
□ 수동 실행 테스트
```

## Phase 4: TradingView
```
□ Indicator 추가
□ Alert 생성
□ Webhook URL 설정 (Render URL)
□ 테스트 신호 확인
```

---

# 🆘 문제 해결

## Render 배포 실패
```
1. 로그 확인: Render Dashboard → Logs
2. requirements.txt 확인
3. Start Command 확인
4. 환경변수 확인
```

## Streamlit 배포 실패
```
1. requirements_streamlit.txt 확인
2. Main file path 확인: dashboard/app.py
3. DATABASE_URL 환경변수 확인
```

## GitHub Actions 실패
```
1. Actions 탭에서 로그 확인
2. Secrets 설정 확인
3. DATABASE_URL 형식 확인
```

## TradingView Webhook 안 옴
```
1. Render 서버 깨우기: https://vmsi-sdm-api.onrender.com/ 접속
2. ngrok 웹 인터페이스 불필요 (공인 URL)
3. Alert 설정 재확인
```

---

# 🚀 다음 단계

1. **지금 바로**: GitHub 저장소 생성 및 푸시
2. **5분**: Render 배포 (FastAPI + PostgreSQL)
3. **3분**: Streamlit Cloud 배포
4. **5분**: GitHub Actions 설정
5. **2분**: TradingView Webhook 연결
6. **완료!**: 24/7 자동화 시스템 가동

---

**총 소요 시간: 약 20분**
**총 비용: $0 (완전 무료)**
**PC 필요: 없음 (클라우드에서 자동 실행)**

---

# 💡 선택사항: Railway (올인원 대안)

Railway는 모든 것을 한 곳에서 관리할 수 있습니다:

## Railway 장점
```
✅ 1개 플랫폼에서 전부 관리
✅ Cron Jobs 내장 (학습 자동화)
✅ PostgreSQL 포함
✅ 쉬운 설정
```

## Railway 단점
```
❌ 무료 크레딧: $5/월
❌ 월말에 크레딧 소진 시 중단
❌ 대시보드 별도 배포 필요 (Streamlit Cloud)
```

## Railway 배포 (선택)
```
1. railway.app 가입
2. "New Project" → "Deploy from GitHub repo"
3. 환경변수 설정
4. PostgreSQL 추가
5. Cron Job 추가
6. 배포!
```

**권장: Render (더 안정적, 완전 무료)**

---

# 📚 추가 자료

- Render Docs: https://render.com/docs
- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Actions Docs: https://docs.github.com/actions
- Railway Docs: https://docs.railway.app

---

**🎯 준비되면 Phase 1부터 시작합니다!**

