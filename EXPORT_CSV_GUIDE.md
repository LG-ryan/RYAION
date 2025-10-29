# TradingView CSV 내보내기 가이드 (30초 완료)

## 🚀 빠른 가이드

### **Step 1: Strategy Tester 열기**
```
1. TradingView.com 접속
2. SPX 차트 열기
3. strategy_sdm_v4_dynamic.pine 추가 (또는 이미 추가됨)
4. 하단 "Strategy Tester" 탭 클릭
```

### **Step 2: List of Trades 탭**
```
Strategy Tester → "List of Trades" 탭 클릭
```

### **Step 3: CSV 내보내기**
```
우클릭 → "Export List..." 또는 "Copy"

파일명: trades_spx_3years.csv
저장 위치: C:\Users\ryanj\RYAION\vmsi-sdm\
```

### **Step 4: 임포트 실행**
```powershell
cd C:\Users\ryanj\RYAION\vmsi-sdm
python tools/import_backtest_signals.py --csv trades_spx_3years.csv --symbol SPX --timeframe 1D --clear
```

**소요 시간: 30초**

---

## ⚡ 또는 아래 명령어로 샘플 데이터 생성:
```
python tools/generate_sample_backtest.py
```


