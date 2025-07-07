FROM python:3.9-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 필요한 폴더 생성
RUN mkdir -p data/uploads data/models data/backups logs

# 소스 코드 복사
COPY src/ ./src/
COPY data/ ./data/

# 포트 노출
EXPOSE 8501

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 애플리케이션 실행
CMD ["streamlit", "run", "src/compressor_system.py", "--server.port=8501", "--server.address=0.0.0.0"]