# VMSI-SDM Python 자동 설치 스크립트
# 관리자 권한 필요

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  VMSI-SDM Python 설치 스크립트" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Python 버전
$pythonVersion = "3.11.6"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"

Write-Host "[1/4] Python $pythonVersion 다운로드 중..." -ForegroundColor Yellow

try {
    # 다운로드
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "  ✓ 다운로드 완료" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ 다운로드 실패: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "수동 설치 방법:" -ForegroundColor Yellow
    Write-Host "  1. https://www.python.org/downloads/ 방문" -ForegroundColor White
    Write-Host "  2. Python 다운로드 및 설치" -ForegroundColor White
    Write-Host "  3. 설치 시 'Add Python to PATH' 체크 필수!" -ForegroundColor White
    pause
    exit 1
}

Write-Host ""
Write-Host "[2/4] Python 설치 중..." -ForegroundColor Yellow
Write-Host "  설치 창이 나타나면 다음 옵션을 선택하세요:" -ForegroundColor Cyan
Write-Host "  ✓ Add Python to PATH (반드시 체크!)" -ForegroundColor Green
Write-Host "  ✓ Install for all users (권장)" -ForegroundColor Green
Write-Host ""
Write-Host "  설치 중... (1-2분 소요)" -ForegroundColor Yellow

# Python 설치 (자동, PATH 추가)
$installArgs = @(
    "/quiet",
    "InstallAllUsers=1",
    "PrependPath=1",
    "Include_test=0"
)

Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait

Write-Host "  ✓ Python 설치 완료" -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] 설치 확인 중..." -ForegroundColor Yellow

# 환경변수 새로고침
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Start-Sleep -Seconds 2

# Python 확인
$pythonCheck = & python --version 2>&1

if ($pythonCheck -match "Python") {
    Write-Host "  ✓ Python 설치 성공: $pythonCheck" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ Python PATH가 아직 적용되지 않았습니다." -ForegroundColor Yellow
    Write-Host "    컴퓨터를 재시작하거나 새 PowerShell 창을 열어주세요." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] 정리 중..." -ForegroundColor Yellow
Remove-Item $installerPath -ErrorAction SilentlyContinue
Write-Host "  ✓ 임시 파일 삭제 완료" -ForegroundColor Green

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ✓ Python 설치 완료!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Yellow
Write-Host "  1. 이 PowerShell 창을 닫으세요" -ForegroundColor White
Write-Host "  2. 새 PowerShell 창을 열어주세요" -ForegroundColor White
Write-Host "  3. vmsi-sdm 폴더로 이동하세요" -ForegroundColor White
Write-Host "  4. setup.bat 를 실행하세요" -ForegroundColor White
Write-Host ""

pause


