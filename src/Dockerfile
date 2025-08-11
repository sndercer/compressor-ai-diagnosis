# 압축기 진단 시스템 - Docker 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p uploads models backups field_uploads reports

# 포트 노출
EXPOSE 8000 8501

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 시작 스크립트 복사 및 실행 권한 부여
COPY start.sh .
RUN chmod +x start.sh

# 애플리케이션 시작
CMD ["./start.sh"]




# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 필요한 디렉토리 생성
RUN mkdir -p uploads models backups field_uploads reports

# 포트 노출
EXPOSE 8000 8501

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 시작 스크립트 복사 및 실행 권한 부여
COPY start.sh .
RUN chmod +x start.sh

# 애플리케이션 시작
CMD ["./start.sh"]


