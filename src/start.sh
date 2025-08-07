#!/bin/bash

# 압축기 진단 시스템 시작 스크립트

echo "🚀 압축기 진단 시스템을 시작합니다..."

# 환경 변수 확인
if [ -z "$KAKAO_CLIENT_ID" ]; then
    echo "⚠️  경고: KAKAO_CLIENT_ID가 설정되지 않았습니다."
fi

if [ -z "$KAKAO_CLIENT_SECRET" ]; then
    echo "⚠️  경고: KAKAO_CLIENT_SECRET이 설정되지 않았습니다."
fi

# 데이터베이스 디렉토리 확인
if [ ! -f "compressor_system.db" ]; then
    echo "📦 데이터베이스를 초기화합니다..."
    python -c "
from backend_api import init_database
init_database()
print('✅ 데이터베이스 초기화 완료')
"
fi

# 백엔드 API 서버 시작 (백그라운드)
echo "🔧 백엔드 API 서버를 시작합니다..."
uvicorn backend_api:app --host 0.0.0.0 --port 8000 &

# API 서버 준비 대기
echo "⏳ API 서버가 준비될 때까지 대기 중..."
while ! curl -f http://localhost:8000/ >/dev/null 2>&1; do
    sleep 1
done
echo "✅ 백엔드 API 서버가 준비되었습니다."

# Streamlit 프론트엔드 시작
echo "🌐 Streamlit 프론트엔드를 시작합니다..."
streamlit run admin_portal.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

# 시그널 처리를 위해 대기
wait


