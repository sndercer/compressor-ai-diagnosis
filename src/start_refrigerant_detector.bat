@echo off
echo.
echo ====================================
echo 🧊 냉매 부족 진단 시스템 시작
echo ====================================
echo.

cd /d "%~dp0"

echo 🔍 시스템 준비 중...
if not exist "refrigerant_recordings" mkdir refrigerant_recordings
if not exist "refrigerant_reports" mkdir refrigerant_reports

echo 🚀 냉매 진단 프로그램을 시작합니다...
echo.
echo 📱 브라우저에서 다음 주소로 접속하세요:
echo    http://localhost:8503
echo.
echo ⚠️  프로그램을 종료하려면 Ctrl+C를 누르세요
echo.

streamlit run refrigerant_leak_detector.py --server.port 8503 --server.address 0.0.0.0

pause
