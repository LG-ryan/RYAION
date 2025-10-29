# TradingView 연결 가이드 (v2.1)

## 🎯 빠른 시작 (10분)

이 가이드를 따라하면 **10분 안에** TradingView와 VMSI-SDM을 완전히 연결할 수 있습니다.

---

## 📋 사전 준비

### 필요한 것
- ✅ TradingView 계정 (무료/유료 모두 가능)
- ✅ 서버 실행 중 (http://localhost:8000)
- ✅ 대시보드 실행 중 (http://localhost:8501)

### 확인하기
```bash
# 서버 상태 확인
curl http://localhost:8000/

# 대시보드 확인
브라우저에서 http://localhost:8501 열기
```

---

## 🚀 Step 1: Indicator 추가 (3분)

### 1.1 TradingView 접속
```
https://www.tradingview.com/chart/
```

### 1.2 Pine Editor 열기
```
화면 하단의 "Pine Editor" 탭 클릭
(없으면 상단 메뉴 → "차트" → "Pine Editor")
```

### 1.3 새 Indicator 생성
```
1) "New" 버튼 클릭
2) "Blank indicator" 선택
```

### 1.4 코드 붙여넣기
```
1) 에디터의 모든 내용 선택 (Ctrl+A)
2) 삭제
3) C:\Users\ryanj\RYAION\vmsi-sdm\pine\indicator_sdm_v2.pine 파일 열기
4) 전체 복사 (Ctrl+A → Ctrl+C)
5) Pine Editor에 붙여넣기 (Ctrl+V)
```

### 1.5 저장 및 적용
```
1) Ctrl+S (또는 "Save" 버튼)
2) 이름: "VMSI-SDM v2.1 Indicator"
3) "Add to Chart" 버튼 클릭
```

### 1.6 확인
```
✅ 차트에 EMA 라인 표시됨
✅ 우측 상단에 패널 표시됨 (Mode, Stage, TrendScore 등)
✅ 배경색 변화 (BUY=녹색, SELL=빨강)
```

---

## 📊 Step 2: Strategy 추가 (3분)

### 2.1 새 Strategy 생성
```
1) Pine Editor → "New" 버튼
2) "Blank strategy" 선택
```

### 2.2 코드 붙여넣기
```
1) C:\Users\ryanj\RYAION\vmsi-sdm\pine\strategy_sdm_v2.pine 파일 열기
2) 전체 복사
3) Pine Editor에 붙여넣기
```

### 2.3 저장 및 적용
```
1) Ctrl+S
2) 이름: "VMSI-SDM v2.1 Strategy"
3) "Add to Chart" 클릭
```

### 2.4 확인
```
✅ 차트 하단에 "Strategy Tester" 패널 나타남
✅ 백테스트 결과 표시 (Net Profit, Win Rate 등)
✅ 차트에 매매 화살표 표시
```

---

## 🔔 Step 3: Alert 설정 (4분)

### 3.1 Alert 생성
```
1) 차트에서 "VMSI-SDM v2.1 Indicator" 우클릭
2) "Add alert..." 선택
```

### 3.2 Alert 설정

#### Condition (조건)
```
VMSI-SDM v2.1 Indicator
   ↓
Any alert() function call
```

#### Options (옵션)
```
✅ "Once Per Bar Close" 체크 (리페인팅 방지)
Expiration: Open-ended (만료 없음)
```

#### Notifications (알림)
```
Webhook URL: http://localhost:8000/alert
(외부 접속: http://your-public-ip:8000/alert)

Message: {{strategy.order.alert_message}}
(자동으로 JSON이 전송됨)
```

### 3.3 Alert 활성화
```
1) "Create" 버튼 클릭
2) Alert 목록에서 활성화 확인 (초록불)
```

### 3.4 테스트
```
1) 차트를 움직여서 신호 발생 유도
2) 서버 로그 확인:
   INFO: 127.0.0.1:xxxx - "POST /alert HTTP/1.1" 200 OK
3) 대시보드에서 신호 확인:
   http://localhost:8501 → "신호 모니터링" 탭
```

---

## ⚙️ Step 4: 설정 최적화 (선택 사항)

### 4.1 Indicator 설정

#### 기본 설정 (초보자)
```
Settings → Inputs:
  ─────────────────────
  Fast Mode: OFF ✅
  Realtime Macro: OFF ✅
  
  EMA1 Length: 20
  EMA2 Length: 50
  RSI Length: 14
  RSI Buy Threshold: 55
  RSI Sell Threshold: 45
```

#### 고급 설정 (경험자)
```
Fast Mode: 시장 상황에 따라 ON/OFF
Realtime Macro: ON (실시간 VIX, DXY 반영)

Alpha: 0.8
Beta: 0.35
Gamma: 0.7
Delta: 0.6
Epsilon: 0.8
```

### 4.2 Strategy 설정

#### 리스크 관리 (강력 추천!)
```
Settings → Inputs → "═ 리스크 관리 ═":
  ─────────────────────
  ✅ Use SL/TP: ON (기본 활성화)
  Stop Loss %: 5.0
  Take Profit %: 10.0
  
  Use ATR-based: OFF (초보자)
                 ON (변동성 높은 시장)
```

#### 포지션 사이징
```
Use Risk-based Position Sizing: OFF (기본)
                                ON (고급)
Risk per Trade: 2.0% (고급 사용자만)
```

---

## 🧪 Step 5: 백테스트 (중요!)

### 5.1 Strategy Tester 확인
```
차트 하단 "Strategy Tester" 탭:
  ─────────────────────
  Net Profit: 총 수익
  Total Closed Trades: 거래 횟수
  Percent Profitable: 승률
  Profit Factor: 수익 팩터
  Max Drawdown: 최대 낙폭
  Avg Trade: 평균 수익
```

### 5.2 성능 평가 기준
```
✅ 좋은 성능:
  - Profit Factor > 1.5
  - Win Rate > 55%
  - Max Drawdown < 15%
  - Avg Win / Avg Loss > 2.0

⚠️ 주의:
  - Profit Factor < 1.0 (손실)
  - Win Rate < 40% (너무 낮음)
  - Max Drawdown > 30% (위험)
```

### 5.3 최적화
```
1) Settings → Inputs에서 파라미터 조정
2) 백테스트 결과 확인
3) 성능 개선될 때까지 반복
4) 최적 파라미터 기록
```

---

## 📱 실제 운용 시작

### 실시간 신호 모니터링
```
1) 대시보드 열기: http://localhost:8501
2) "신호 모니터링" 탭 확인
3) 신호 발생 시 실시간 표시됨
```

### 서버 로그 모니터링
```
터미널에서 확인:
  INFO: POST /alert - 200 OK
  [OK] Labeled signal 1 (BTCUSDT BUY)
```

### Alert 수신 확인
```
TradingView 우측 상단 종 아이콘:
  - Alert 발생 기록 확인
  - Webhook 전송 성공 여부 확인
```

---

## 🔧 문제 해결

### Q1: Alert가 전송되지 않아요
```
✅ 확인사항:
  1. Alert "Create" 버튼 눌렀나요?
  2. Alert 목록에서 활성화(초록불) 되어있나요?
  3. Webhook URL이 정확한가요?
  4. 서버가 실행 중인가요? (http://localhost:8000)
  5. 방화벽에서 8000 포트가 열려있나요?

🔍 테스트:
  # 서버 직접 테스트
  curl -X POST http://localhost:8000/alert \
    -H "Content-Type: application/json" \
    -d '{"symbol":"TEST","signal":"BUY"}'
```

### Q2: Indicator가 차트에 안 보여요
```
✅ 확인사항:
  1. "Add to Chart" 버튼 눌렀나요?
  2. 차트 왼쪽 상단에 "VMSI-SDM v2.1" 표시되나요?
  3. Pine Editor에서 컴파일 에러 없나요?
  
🔍 해결:
  - 차트 좌측 상단에서 Indicator 클릭
  - "Settings" → "Style" 탭에서 표시 옵션 확인
```

### Q3: 백테스트 결과가 이상해요
```
✅ 확인사항:
  1. 충분한 기간의 데이터인가요? (최소 6개월)
  2. SL/TP가 너무 타이트하지 않나요?
  3. Commission(수수료) 설정이 현실적인가요?
  
🔍 개선:
  - Settings → Properties에서:
    - Initial Capital: 100000
    - Commission: 0.1% (현물), 0.05% (선물)
    - Slippage: 1 tick
```

### Q4: 신호가 너무 많아요 / 적어요
```
✅ 너무 많을 때:
  - Fast Mode OFF로 변경
  - Cooldown Bars 증가 (3 → 5)
  - RSI Threshold 조정 (Buy: 55→60, Sell: 45→40)

✅ 너무 적을 때:
  - Fast Mode ON으로 변경
  - Cooldown Bars 감소 (3 → 1)
  - RSI Threshold 완화 (Buy: 55→50, Sell: 45→50)
```

### Q5: 외부에서 Webhook 접속이 안돼요
```
✅ 로컬 테스트용:
  - Webhook URL: http://localhost:8000/alert
  
✅ 외부 접속용 (2가지 방법):
  
  방법 1) 포트 포워딩:
    1. 공유기 관리 페이지 접속
    2. 포트 포워딩 설정: 8000 → PC IP
    3. Webhook URL: http://공인IP:8000/alert
  
  방법 2) ngrok 사용 (권장):
    1. ngrok 다운로드: https://ngrok.com/
    2. 실행: ngrok http 8000
    3. Forwarding URL 복사: https://xxxx.ngrok.io
    4. Webhook URL: https://xxxx.ngrok.io/alert
```

---

## 📊 권장 심볼 및 타임프레임

### 초보자
```
심볼: BINANCE:BTCUSDT
타임프레임: 15분, 1시간
이유: 유동성 높고, 신호 빈도 적당
```

### 중급자
```
심볼: SPY, QQQ, TSLA (미국 주식)
타임프레임: 5분, 15분, 1시간
이유: 변동성 적당, 백테스트 데이터 풍부
```

### 고급자
```
심볼: 관심 종목
타임프레임: 1분~일봉 (전략에 따라)
설정: Fast Mode, Realtime Macro ON
```

---

## 🎓 다음 단계

### 1주차: 모니터링
```
- 신호 발생 패턴 관찰
- 대시보드에서 성과 추적
- 백테스트 결과와 실제 비교
```

### 2주차: 최적화
```
- 파라미터 미세 조정
- 다양한 심볼/타임프레임 테스트
- Optuna 학습 실행 (고급)
```

### 3주차: 실전
```
- 소액으로 실거래 시작
- 리스크 관리 철저히
- 지속적인 모니터링
```

---

## 📚 추가 자료

### 문서
```
- docs/IMPROVEMENTS_v2.1.md: 개선 사항 상세
- docs/UPGRADE_GUIDE.md: 업그레이드 가이드
- docs/EVALUATION_Codex_vs_Cursor.md: 기술 평가
```

### 커뮤니티
```
- TradingView Pine Script: https://www.tradingview.com/pine-script-docs/
- VMSI-SDM GitHub: (프로젝트 링크)
```

---

## ✅ 체크리스트

완료한 항목에 체크하세요:

### 기본 설정
- [ ] Indicator 추가 완료
- [ ] Strategy 추가 완료
- [ ] Alert 생성 완료
- [ ] Webhook 연결 완료

### 테스트
- [ ] 서버에서 Alert 수신 확인
- [ ] 대시보드에서 신호 표시 확인
- [ ] 백테스트 결과 확인
- [ ] 성능 지표 만족스러움

### 최적화
- [ ] 파라미터 조정 완료
- [ ] 리스크 관리 설정 완료
- [ ] 실시간 모니터링 준비 완료

---

## 🎉 완료!

모든 단계를 완료하셨다면 **VMSI-SDM 자가학습형 트레이딩 시스템**이 완벽하게 연결되었습니다!

### 다음은?
```
A) Optuna 학습 실행 → 파라미터 자동 최적화
B) 더 많은 테스트 신호 수집 → 데이터 축적
C) 다른 심볼/타임프레임 적용
D) 실전 운용 시작 (소액)
```

**Happy Trading! 🚀**

---

**가이드 버전**: v2.1  
**최종 업데이트**: 2025-10-29  
**문의**: docs/README.md 참고

