# tv_export.py
# ✅ 일반 ChromeDriver 방식 (안정적!)
# 프로필 복사본을 사용해서 로그인 상태 유지
# 
# 📌 사용법: START_HERE.bat 더블클릭

import os, time, urllib.parse, json, shutil
from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===== 설정 =====
TIMEFRAME = "1D"  # "1D", "240"(4H), "1W" 등
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = str(BASE_DIR / "exports")
PROGRESS_FILE = str(BASE_DIR / "progress.json")
DEBUG_LOG = str(BASE_DIR / "debug.log")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_RETRIES = 2  # 각 티커당 최대 재시도 횟수

# 워치리스트(최종)
TICKERS = [
    "AMEX:IWM","NASDAQ:MSTR","NASDAQ:NVDA","NASDAQ:TSLA","NASDAQ:NFLX","NYSE:SMR",
    "NASDAQ:COIN","AMEX:BMNR","NASDAQ:QQQ","NASDAQ:TQQQ","NASDAQ:SQQQ","SP:SPX",
    "KRX:KOSPI","CBOE:SVIX","BINANCE:BTCUSDT","BINANCE:ETHUSDT","TVC:USOIL","AMEX:XLE",
    "COMEX:GC1!","AMEX:GLD","COMEX:HG1!","NASDAQ:TLT","AMEX:VNQ","AMEX:XLU","TVC:DXY",
    "AMEX:FXI","AMEX:EEM","AMEX:EWJ","AMEX:EWG","AMEX:XLV","AMEX:XLP","NYSE:JNJ","NYSE:PG",
    "AMEX:XLF","AMEX:XHB","CBOE:VIXY","AMEX:DBC","FOREXCOM:CORN"
]

# ===== 로깅 =====
def debug_log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)

# ===== 프로필 관리 =====
def get_chrome_profile():
    """Chrome 프로필 준비 (한 번만 복사하고 재사용)"""
    original = Path.home() / "AppData/Local/Google/Chrome/User Data/Default"
    copied = Path(os.environ['TEMP']) / "ChromeProfile_TVExport"
    
    debug_log(f"\n📋 Chrome 프로필 준비 중...")
    
    # 복사본이 이미 있으면 재사용
    if copied.exists():
        debug_log(f"   ✅ 기존 프로필 재사용 (복사 시간 0초)")
        debug_log(f"   경로: {copied}")
        debug_log(f"   💡 새로 복사하려면 delete_profile.bat 실행 후 다시 시작")
        return str(copied), True
    
    # 원본 프로필 확인
    if not original.exists():
        debug_log(f"   ❌ 원본 프로필이 없습니다!")
        debug_log(f"   → 빈 프로필 생성 (수동 로그인 필요)")
        copied.mkdir(parents=True, exist_ok=True)
        return str(copied), False
    
    # 최초 1회만 복사
    try:
        debug_log(f"   최초 실행: 프로필 복사 시작... (약 10-30초)")
        debug_log(f"   ⏳ 잠시만 기다려주세요... (다음부턴 즉시 시작)")
        shutil.copytree(original, copied, ignore_dangling_symlinks=True)
        debug_log(f"   ✅ 프로필 복사 완료!")
        debug_log(f"   📌 다음 실행부터는 복사 없이 바로 시작됩니다!")
        return str(copied), True
    except Exception as e:
        debug_log(f"   ⚠️ 프로필 복사 실패: {e}")
        debug_log(f"   → 빈 프로필 생성 (수동 로그인 필요)")
        copied.mkdir(parents=True, exist_ok=True)
        return str(copied), False

# ===== Chrome 설정 =====
debug_log("\n" + "=" * 60)
debug_log("🚀 TradingView 차트 데이터 자동 다운로드")
debug_log("=" * 60)

profile_path, has_login = get_chrome_profile()

chrome_options = Options()
chrome_options.add_argument(f'--user-data-dir={profile_path}')
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--log-level=3")  # 오류 로그 숨기기
chrome_options.add_argument("--silent")  # Chrome 내부 메시지 숨기기

prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
chrome_options.add_experimental_option("useAutomationExtension", False)

debug_log("\n🔧 ChromeDriver 실행 중...")

# chromedriver.exe 경로 설정 (환경변수에 추가)
if Path("chromedriver.exe").exists():
    chromedriver_path = str(Path("chromedriver.exe").resolve())
    os.environ['PATH'] = f"{Path.cwd()};{os.environ['PATH']}"
    debug_log(f"   ChromeDriver: {chromedriver_path}")

try:
    # 단순하게 options만 전달 (Selenium 3.x/4.x 모두 호환)
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    debug_log("✅ Chrome 실행 성공!")
    
    # 창 최대화 (중요: 화면에 보이는 만큼 데이터 로드됨!)
    driver.maximize_window()
    debug_log("🖥️  Chrome 창 최대화 완료")
    
    if not has_login:
        debug_log("\n⚠️  프로필 복사 실패 - 수동 로그인이 필요합니다!")
    
except Exception as e:
    debug_log(f"❌ Chrome 실행 실패: {e}")
    debug_log("\n💡 해결 방법:")
    debug_log("  1. Chrome이 설치되어 있는지 확인")
    debug_log("  2. pip install --upgrade selenium")
    debug_log("  3. ChromeDriver 자동 다운로드 대기 (처음 실행 시)")
    input("\n아무 키나 눌러 종료...")
    exit(1)

# ===== 유틸 함수들 =====
def open_chart(symbol: str):
    # Ryan's signal 레이아웃 차트 ID 사용
    base = "https://www.tradingview.com/chart/4zGU1iHd/"
    q = f"?symbol={urllib.parse.quote(symbol)}&interval={urllib.parse.quote(TIMEFRAME)}"
    driver.get(base + q)

def set_custom_date_range(years=20):
    """캘린더에서 Custom range 설정 (최근 N년 데이터)"""
    from datetime import datetime, timedelta
    from selenium.webdriver.common.keys import Keys
    
    try:
        # 1. 캘린더 버튼 클릭 (빠르게!)
        debug_log(f"         캘린더 버튼 찾는 중...")
        
        # WebDriverWait를 짧게 (5초)
        short_wait = WebDriverWait(driver, 5)
        
        calendar_btn = None
        selectors = [
            'button[aria-label="Go to"]',
            'button[data-tooltip="Go to >"]',
        ]
        
        for sel in selectors:
            try:
                calendar_btn = short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
                debug_log(f"         캘린더 버튼 찾음")
                break
            except:
                continue
        
        if not calendar_btn:
            raise Exception("캘린더 버튼을 찾을 수 없음")
        
        calendar_btn.click()
        time.sleep(1)  # 2초 → 1초
        
        # 2. "Custom range" 탭 클릭 (빠르게!)
        debug_log(f"         Custom range 탭 클릭 중...")
        
        found = False
        xpaths = [
            "//div[text()='Custom range']",
            "//*[text()='Custom range']",
        ]
        
        for xpath in xpaths:
            try:
                tab = short_wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                tab.click()
                time.sleep(0.5)  # 1초 → 0.5초
                found = True
                break
            except:
                continue
        
        if not found:
            raise Exception("Custom range 탭을 찾을 수 없음")
        
        # 3. 날짜 계산
        today = datetime.now()
        from_date = today - timedelta(days=years*365)
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = today.strftime("%Y-%m-%d")
        
        debug_log(f"         기간 설정: {from_date_str} ~ {to_date_str} ({years}년)")
        
        # 4. From/To 날짜 입력 (빠르게!)
        try:
            # From 날짜 (시작일)
            from_input = short_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[data-name='start-date-range']")
            ))
            from_input.click()
            time.sleep(0.3)
            from_input.send_keys(Keys.CONTROL + "a")
            from_input.send_keys(Keys.DELETE)
            time.sleep(0.2)
            from_input.send_keys(from_date_str)
            debug_log(f"            시작일 입력: {from_date_str}")
            time.sleep(0.3)
            
            # To 날짜 (종료일)
            to_input = short_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[data-name='end-date-range']")
            ))
            to_input.click()
            time.sleep(0.3)
            to_input.send_keys(Keys.CONTROL + "a")
            to_input.send_keys(Keys.DELETE)
            time.sleep(0.2)
            to_input.send_keys(to_date_str)
            debug_log(f"            종료일 입력: {to_date_str}")
            time.sleep(0.5)
            
            # Enter 키로 바로 실행 (Go to 버튼 클릭보다 빠름!)
            debug_log(f"         Enter 키로 실행 중...")
            to_input.send_keys(Keys.RETURN)
            debug_log(f"         ✅ Custom range 실행 완료!")
            
        except Exception as e:
            raise Exception(f"날짜 입력 또는 실행 실패: {e}")
        
        # 6. 데이터 로딩 대기 (엔터 후 차트 반영 시간)
        debug_log(f"         ⏳ {years}년 데이터 로딩 중...")
        time.sleep(2)  # 실제 반영 시간: 1-2초
        debug_log(f"         ✅ 데이터 로드 완료!")
        
        return True  # 성공
        
    except Exception as e:
        debug_log(f"         ⚠️ Custom range 설정 실패: {e}")
        debug_log(f"         → 기본 범위로 진행합니다")
        return False

def click_chart_menu():
    """레이아웃 드롭다운 버튼 클릭 (Ryan's signal ▼)"""
    
    # 레이아웃 드롭다운 버튼 셀렉터들
    selectors = [
        'button[data-name="save-load-menu"]',  # ← 정확한 셀렉터!
        'button[aria-label="Manage layouts"]',
        '[data-name="save-load-menu"]',
        'button[data-tooltip="Manage layouts"]',
        'button[aria-label="레이아웃 관리"]',
    ]
    
    for sel in selectors:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            debug_log(f"         Manage layouts 버튼 찾음: {sel}")
            btn.click()
            time.sleep(1)
            return
        except Exception:
            continue
    
    # XPath로 시도
    xpaths = [
        '//button[contains(text(),"Manage layouts")]',
        '//button[contains(text(),"레이아웃 관리")]',
        '//button[@data-name="manage-layouts"]',
        '//button[contains(@aria-label,"layout")]',
        '//button[contains(@aria-label,"Layout")]',
    ]
    
    for xp in xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            debug_log(f"         Manage layouts 버튼 찾음 (XPath): {xp}")
            btn.click()
            time.sleep(1)
            return
        except Exception:
            continue
    
    # 모든 버튼에서 "layout" 텍스트 찾기
    try:
        debug_log("         모든 버튼에서 'layout' 검색 중...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            try:
                text = btn.text
                aria_label = btn.get_attribute("aria-label")
                data_name = btn.get_attribute("data-name")
                
                if text and "layout" in text.lower():
                    debug_log(f"         Manage layouts 버튼 찾음: text={text}")
                    btn.click()
                    time.sleep(1)
                    return
                if aria_label and "layout" in aria_label.lower():
                    debug_log(f"         Manage layouts 버튼 찾음: aria-label={aria_label}")
                    btn.click()
                    time.sleep(1)
                    return
                if data_name and "layout" in data_name.lower():
                    debug_log(f"         Manage layouts 버튼 찾음: data-name={data_name}")
                    btn.click()
                    time.sleep(1)
                    return
            except:
                continue
    except:
        pass
    
    raise RuntimeError("Manage layouts 버튼을 찾지 못했습니다.")

def click_export_item():
    """Export chart data 메뉴 항목 클릭"""
    
    # CSS 셀렉터들
    selectors = [
        'span.label-jFqVJdrK',  # 정확한 클래스명
        '[class*="label"]',
    ]
    
    for sel in selectors:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, sel)
            for item in items:
                if "Export chart data" in item.text:
                    debug_log(f"         Export chart data 찾음: {sel}")
                    item.click()
                    time.sleep(1)
                    return
        except Exception:
            continue
    
    # XPath로 시도
    xpaths = [
        '//span[contains(text(),"Export chart data")]',
        '//span[text()="Export chart data"]',
        '//span[contains(@class,"label")]//span[contains(text(),"Export")]',
        '//div[contains(@class,"itemRow")]//span[contains(text(),"Export chart data")]',
        '//div[contains(@role,"menuitem")]//span[contains(text(),"Export chart data")]',
    ]
    
    for xp in xpaths:
        try:
            item = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            debug_log(f"         Export chart data 찾음 (XPath): {xp}")
            item.click()
            time.sleep(1)
            return
        except Exception:
            continue
    
    raise RuntimeError("Export chart data 항목을 찾지 못했습니다.")

def confirm_export_dialog():
    xpaths = [
        '//button[.//span[contains(text(),"Export")]]',
        '//button[.//span[contains(text(),"내보내기")]]',
        '//button[@data-name="dialog-ok"]',
    ]
    for xp in xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            btn.click()
            return
        except Exception:
            continue
    raise RuntimeError("Export 버튼을 찾지 못했습니다.")

def wait_for_download_complete(timeout=30):
    """다운로드가 완료될 때까지 대기"""
    seconds = 0
    while seconds < timeout:
        downloading = list(Path(DOWNLOAD_DIR).glob("*.crdownload"))
        if not downloading:
            time.sleep(1)  # 파일 쓰기 완료 대기
            return True
        time.sleep(1)
        seconds += 1
    return False

def rename_latest_download(symbol: str):
    if not wait_for_download_complete():
        return False
    
    files = [f for f in Path(DOWNLOAD_DIR).glob("*") if f.suffix == ".csv"]
    if not files:
        return False
    
    latest = max(files, key=lambda p: p.stat().st_mtime)
    target = Path(DOWNLOAD_DIR) / f"{symbol.replace(':','_')}_{TIMEFRAME}.csv"
    
    try:
        if target.exists():
            target.unlink()
        latest.rename(target)
        return True
    except:
        return False

def export_one_symbol(symbol: str, retry=0):
    """한 티커의 데이터를 내보내기"""
    try:
        debug_log(f"      → 차트 열기 시도...")
        open_chart(symbol)
        time.sleep(3)  # 페이지 로딩 대기
        
        debug_log(f"      → 차트 컨테이너 확인...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.chart-container')))
        time.sleep(2)  # 차트 렌더링 대기
        
        # Watchlist 닫기 (화면 공간 확보) - 필수! 찾을 때까지 계속 시도!
        debug_log(f"      → Watchlist 패널 닫기 시작...")
        
        watchlist_closed = False
        attempt = 0
        
        while not watchlist_closed:
            attempt += 1
            if attempt > 1:
                debug_log(f"         🔄 재시도 {attempt}회차... (5초 후)")
                time.sleep(5)
            
            try:
                # JavaScript로 상세 정보 수집 & 버튼 찾기
                result = driver.execute_script("""
                    // 1. 여러 방법으로 버튼 찾기
                    var btn = document.querySelector('button[data-name="right-toolbar"]');
                    if (!btn) btn = document.querySelector('button[role="toolbar"][aria-pressed="true"]');
                    if (!btn) btn = document.querySelector('button[aria-label*="Watchlist"]');
                    
                    // 2. 페이지 정보 수집 (디버깅용)
                    var allButtons = document.querySelectorAll('button').length;
                    var toolbarButtons = Array.from(document.querySelectorAll('button')).filter(b => {
                        var dataName = b.getAttribute('data-name') || '';
                        var ariaLabel = b.getAttribute('aria-label') || '';
                        return dataName.includes('toolbar') || ariaLabel.toLowerCase().includes('watchlist');
                    });
                    
                    // 3. 버튼 못 찾은 경우
                    if (!btn) {
                        return {
                            found: false, 
                            totalButtons: allButtons,
                            toolbarButtonsCount: toolbarButtons.length,
                            toolbarButtonsInfo: toolbarButtons.slice(0, 3).map(b => ({
                                'data-name': b.getAttribute('data-name'),
                                'aria-label': b.getAttribute('aria-label')
                            }))
                        };
                    }
                    
                    // 4. 버튼 찾은 경우 - 상태 확인 & 클릭
                    var btnClass = btn.className || "";
                    var wasActive = btnClass.includes('isActive-');
                    
                    if (wasActive) {
                        btn.click();
                    }
                    
                    // 5. 최종 상태 확인
                    var finalClass = btn.className || "";
                    var isStillActive = finalClass.includes('isActive-');
                    
                    return {
                        found: true,
                        className: btnClass.substring(0, 100),
                        wasActive: wasActive, 
                        clicked: wasActive,
                        isStillActive: isStillActive,
                        finalClosed: !isStillActive,
                        totalButtons: allButtons
                    };
                """)
                
                # 상세 로그 출력
                if not result.get('found'):
                    debug_log(f"         ⚠️ {attempt}회 시도: 버튼 못 찾음!")
                    debug_log(f"            - 전체 버튼 개수: {result.get('totalButtons', '?')}")
                    debug_log(f"            - Toolbar 관련 버튼: {result.get('toolbarButtonsCount', '?')}개")
                    if result.get('toolbarButtonsInfo'):
                        for idx, info in enumerate(result.get('toolbarButtonsInfo', [])):
                            debug_log(f"            - 버튼 {idx+1}: data-name='{info.get('data-name')}', aria-label='{info.get('aria-label')}'")
                    continue  # 다시 시도
                
                debug_log(f"         ✅ 버튼 찾음!")
                debug_log(f"            - className: {result.get('className', 'N/A')[:60]}...")
                debug_log(f"            - 열려있었나? {result.get('wasActive', False)}")
                
                if result.get('clicked'):
                    debug_log(f"         📋 Watchlist 열려있었음 - 닫기 클릭")
                    time.sleep(1)
                
                # 최종 상태 검증
                if result.get('finalClosed'):
                    debug_log(f"         ✅ Watchlist 닫힌 상태 확인 완료!")
                    watchlist_closed = True
                    break
                else:
                    debug_log(f"         ⚠️ {attempt}회 시도: 여전히 열려있음!")
                    debug_log(f"            - 클릭했나? {result.get('clicked', False)}")
                    debug_log(f"            - 현재 className: {result.get('className', 'N/A')[:60]}...")
                    continue
                    
            except Exception as e:
                debug_log(f"         ⚠️ {attempt}회 시도 JavaScript 실패: {str(e)[:60]}")
        
        # 전체화면 모드 시도 (더 많은 데이터 표시를 위해)
        try:
            debug_log(f"      → 전체화면 모드 활성화 중...")
            # F11 키로 브라우저 전체화면
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F11)
            time.sleep(2)
            debug_log(f"         ✅ 전체화면 모드 활성화")
        except Exception as e:
            debug_log(f"         ⚠️ 전체화면 모드 실패 (계속 진행): {e}")
            pass
        
        time.sleep(1)
        
        # Custom range로 최근 15년 데이터 로드 (약 3780 bars, 안전)
        debug_log(f"      → 최근 15년 데이터 로드 시작...")
        range_success = set_custom_date_range(years=15)
        
        if not range_success:
            debug_log(f"      ⚠️ Custom range 설정 실패! 재시도...")
            time.sleep(3)
            range_success = set_custom_date_range(years=15)
            
            if not range_success:
                raise Exception("Custom range 설정 2회 실패 - 티커 스킵")
        
        debug_log(f"      ✅ 15년 데이터 로드 완료 확인!")
        
        # Manage layouts 버튼 클릭 (정확한 셀렉터 사용)
        debug_log(f"      → Manage layouts 버튼 클릭...")
        click_chart_menu()
        
        debug_log(f"      → Export chart data 클릭...")
        click_export_item()
        
        debug_log(f"      → Export 확인...")
        confirm_export_dialog()
        
        debug_log(f"      → 다운로드 대기...")
        if rename_latest_download(symbol):
            print(f"  ✅ 성공")
            return True
        else:
            raise Exception("파일 저장 실패")
    except Exception as e:
        debug_log(f"      ❌ 에러: {str(e)}")
        if retry < MAX_RETRIES:
            print(f"  ⚠️ 재시도 {retry + 1}/{MAX_RETRIES}: {str(e)[:30]}")
            time.sleep(2)
            return export_one_symbol(symbol, retry + 1)
        else:
            print(f"  ❌ 최종 실패: {str(e)[:50]}")
            return False

def save_progress(completed, failed):
    """진행상황 저장"""
    progress = {
        "last_run": datetime.now().isoformat(),
        "completed": completed,
        "failed": failed,
        "total": len(TICKERS)
    }
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

# ===== 메인 =====
def main():
    open_chart(TICKERS[0])
    
    # 로그인 확인
    print("\n" + "=" * 60)
    print("⚠️  로그인 확인 (중요!)")
    print("=" * 60)
    print("\nChrome 창을 확인하세요:")
    print("  1. TradingView에 로그인되어 있나요?")
    print("  2. 로그인 안 되어 있다면:")
    print("     → 지금 수동으로 로그인하세요!")
    print("     → 인디케이터도 차트에 추가하세요")
    print("     → 타임프레임을 1D로 설정하세요")
    print("\n로그인 완료되면 Enter를 누르세요...")
    input()
    
    completed = []
    failed = []
    
    debug_log("\n" + "=" * 60)
    debug_log(f"📥 {len(TICKERS)}개 티커 다운로드 시작...")
    debug_log("=" * 60 + "\n")
    
    for i, sym in enumerate(TICKERS, 1):
        print(f"[{i}/{len(TICKERS)}] {sym}", end=" ")
        
        if export_one_symbol(sym):
            completed.append(sym)
        else:
            failed.append(sym)
        
        save_progress(completed, failed)
    
    # 최종 결과
    debug_log("\n" + "=" * 60)
    debug_log("✅ 다운로드 완료!")
    debug_log("=" * 60)
    debug_log(f"📊 결과:")
    debug_log(f"   성공: {len(completed)}/{len(TICKERS)}")
    debug_log(f"   실패: {len(failed)}/{len(TICKERS)}")
    
    if failed:
        debug_log(f"\n❌ 실패한 티커 ({len(failed)}개):")
        for sym in failed:
            debug_log(f"   - {sym}")
    
    debug_log(f"\n📁 CSV 파일: {DOWNLOAD_DIR}")
    debug_log(f"💾 진행상황: {PROGRESS_FILE}")
    debug_log(f"📝 디버그 로그: {DEBUG_LOG}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        debug_log("\n\n⚠️ 사용자가 중단했습니다.")
    except Exception as e:
        debug_log(f"\n\n❌ 예상치 못한 오류: {e}")
        import traceback
        debug_log(traceback.format_exc())
    finally:
        debug_log(f"\n종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        input("\n아무 키나 눌러 종료...")
        try:
            driver.quit()
        except:
            pass
