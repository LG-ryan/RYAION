"""대시보드 재시작 스크립트"""
import os
import signal
import psutil
import time

print("Restarting Streamlit dashboard...")

# Streamlit 프로세스 종료
killed = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info.get('cmdline', [])
        if cmdline and any('streamlit' in str(cmd).lower() for cmd in cmdline):
            print(f"Killing process {proc.info['pid']}: {proc.info['name']}")
            proc.kill()
            killed = True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if killed:
    print("Waiting for process to terminate...")
    time.sleep(2)

# 새로운 Streamlit 시작
print("\nStarting new Streamlit instance...")
print("Dashboard will be available at: http://localhost:8501")
print("\nPlease run this command in a new terminal:")
print("  cd C:\\Users\\ryanj\\RYAION\\vmsi-sdm")
print("  python -m streamlit run dashboard\\app.py")


