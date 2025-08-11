# 🚀 배포 가이드

압축기 진단 시스템을 GitHub에서 배포하는 방법을 안내합니다.

## 📋 배포 전 체크리스트

### 1. 카카오톡 개발자 센터 설정

1. [카카오 개발자 센터](https://developers.kakao.com/) 접속
2. 새 애플리케이션 생성
3. **앱 설정 > 플랫폼** 에서 Web 플랫폼 추가
4. **제품 설정 > 카카오 로그인** 활성화
5. **제품 설정 > 카카오 로그인 > Redirect URI** 설정:
   ```
   개발: http://localhost:8501/auth/kakao/callback
   프로덕션: https://your-domain.com/auth/kakao/callback
   ```
6. **제품 설정 > 카카오 로그인 > 동의항목** 설정:
   - 닉네임: 필수 동의
   - 프로필 사진: 선택 동의
   - 이메일: 선택 동의

### 2. 필요한 정보 수집

- **JavaScript 키** (Client ID)
- **REST API 키** (Client Secret 용도)
- **Admin 키** (선택사항)

## 🔧 GitHub 저장소 설정

### 1. 저장소 생성

```bash
# GitHub에서 새 저장소 생성 후
git clone https://github.com/your-username/compressor-ai-diagnosis.git
cd compressor-ai-diagnosis

# 프로젝트 파일 복사
# (현재 프로젝트의 모든 파일을 새 저장소로 복사)

git add .
git commit -m "Initial commit: 압축기 진단 시스템"
git push origin main
```

### 2. GitHub Secrets 설정

**Settings > Secrets and variables > Actions**에서 다음 변수들을 설정:

#### Repository Secrets
```
KAKAO_CLIENT_ID=your-javascript-key-here
KAKAO_CLIENT_SECRET=your-rest-api-key-here
SECRET_KEY=your-super-secret-jwt-key-here-change-this
```

#### Environment Variables (선택사항)
```
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure-password-123
PRODUCTION_URL=https://your-domain.com
```

### 3. GitHub Container Registry 권한 설정

1. **Settings > Actions > General**
2. **Workflow permissions**에서 "Read and write permissions" 선택
3. "Allow GitHub Actions to create and approve pull requests" 체크

## 🐳 Docker 배포

### 로컬 테스트

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일 편집 (카카오톡 키 입력)
nano .env

# Docker Compose로 실행
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
docker-compose logs compressor-diagnosis
```

### 접속 확인

- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **프론트엔드**: http://localhost:8501

## ☁️ 클라우드 배포

### GitHub Container Registry

```bash
# 자동 배포 (main 브랜치 푸시 시)
git push origin main

# 수동 배포
docker build -t ghcr.io/your-username/compressor-diagnosis:latest .
echo $GITHUB_TOKEN | docker login ghcr.io -u your-username --password-stdin
docker push ghcr.io/your-username/compressor-diagnosis:latest
```

### AWS 배포 (예시)

```bash
# AWS CLI 설정
aws configure

# ECR 저장소 생성
aws ecr create-repository --repository-name compressor-diagnosis

# 이미지 태깅 및 푸시
docker tag ghcr.io/your-username/compressor-diagnosis:latest \
  your-account.dkr.ecr.region.amazonaws.com/compressor-diagnosis:latest

aws ecr get-login-password --region region | \
  docker login --username AWS --password-stdin \
  your-account.dkr.ecr.region.amazonaws.com

docker push your-account.dkr.ecr.region.amazonaws.com/compressor-diagnosis:latest

# ECS 서비스 배포
aws ecs update-service --cluster your-cluster --service compressor-diagnosis --force-new-deployment
```

### Google Cloud Run 배포 (예시)

```bash
# gcloud CLI 설정
gcloud auth login
gcloud config set project your-project-id

# 이미지 태깅
docker tag ghcr.io/your-username/compressor-diagnosis:latest \
  gcr.io/your-project-id/compressor-diagnosis:latest

# 이미지 푸시
docker push gcr.io/your-project-id/compressor-diagnosis:latest

# Cloud Run 배포
gcloud run deploy compressor-diagnosis \
  --image gcr.io/your-project-id/compressor-diagnosis:latest \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars KAKAO_CLIENT_ID=$KAKAO_CLIENT_ID \
  --set-env-vars KAKAO_CLIENT_SECRET=$KAKAO_CLIENT_SECRET \
  --set-env-vars SECRET_KEY=$SECRET_KEY
```

## 🔒 보안 설정

### 1. HTTPS 설정 (프로덕션 필수)

```bash
# Let's Encrypt 인증서 (nginx 예시)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 환경 변수 보안

```bash
# .env 파일 절대 Git에 커밋하지 않기
echo ".env" >> .gitignore

# 프로덕션에서는 시스템 환경 변수 사용
export KAKAO_CLIENT_ID="your-key"
export KAKAO_CLIENT_SECRET="your-secret"
export SECRET_KEY="your-jwt-secret"
```

### 3. 카카오톡 리다이렉트 URI 업데이트

프로덕션 배포 후 카카오 개발자 센터에서:
```
https://your-domain.com/auth/kakao/callback
```

## 📊 모니터링 설정

### 헬스체크 확인

```bash
# API 서버 상태 확인
curl http://your-domain.com:8000/

# 응답 예시
{"message":"압축기 진단 API 서버","version":"1.0.0"}
```

### 로그 모니터링

```bash
# Docker 로그 확인
docker logs compressor-diagnosis-compressor-diagnosis-1 --follow

# 시스템 로그 (Linux)
tail -f /var/log/syslog
```

## 🔄 업데이트 배포

### 자동 배포 (권장)

```bash
# 코드 변경 후
git add .
git commit -m "기능 개선: 새로운 진단 알고리즘 추가"
git push origin main

# GitHub Actions가 자동으로 빌드 및 배포
```

### 수동 배포

```bash
# 새 이미지 빌드
docker build -t ghcr.io/your-username/compressor-diagnosis:v2.0.0 .

# 푸시
docker push ghcr.io/your-username/compressor-diagnosis:v2.0.0

# 서비스 업데이트
docker-compose pull
docker-compose up -d
```

## 🚨 문제 해결

### 일반적인 문제들

1. **카카오톡 로그인 실패**
   ```bash
   # 설정 확인
   python kakao_config.py
   
   # 리다이렉트 URI 확인
   # 개발: http://localhost:8501/auth/kakao/callback
   # 프로덕션: https://your-domain.com/auth/kakao/callback
   ```

2. **Docker 이미지 빌드 실패**
   ```bash
   # 캐시 클리어 후 재빌드
   docker system prune -f
   docker build --no-cache -t compressor-diagnosis .
   ```

3. **데이터베이스 연결 오류**
   ```bash
   # 권한 확인
   ls -la compressor_system.db
   
   # 디렉토리 권한 설정
   chmod 755 ./
   chmod 644 compressor_system.db
   ```

### 로그 수집

```bash
# 모든 컨테이너 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs compressor-diagnosis

# 실시간 로그 추적
docker-compose logs -f compressor-diagnosis
```

## 📞 지원

문제가 지속되면:

1. GitHub Issues에 문제 보고
2. 로그 파일 첨부
3. 환경 정보 (OS, Docker 버전 등) 포함

## ✅ 배포 성공 확인

1. ✅ 웹사이트 접속 가능
2. ✅ 카카오톡 로그인 작동
3. ✅ 파일 업로드 및 진단 기능 정상
4. ✅ 관리자 포털 접근 가능
5. ✅ API 문서 접근 가능 (`/docs`)

---

🎉 배포 완료! 이제 사용자들이 압축기 진단 시스템을 사용할 수 있습니다.



압축기 진단 시스템을 GitHub에서 배포하는 방법을 안내합니다.

## 📋 배포 전 체크리스트

### 1. 카카오톡 개발자 센터 설정

1. [카카오 개발자 센터](https://developers.kakao.com/) 접속
2. 새 애플리케이션 생성
3. **앱 설정 > 플랫폼** 에서 Web 플랫폼 추가
4. **제품 설정 > 카카오 로그인** 활성화
5. **제품 설정 > 카카오 로그인 > Redirect URI** 설정:
   ```
   개발: http://localhost:8501/auth/kakao/callback
   프로덕션: https://your-domain.com/auth/kakao/callback
   ```
6. **제품 설정 > 카카오 로그인 > 동의항목** 설정:
   - 닉네임: 필수 동의
   - 프로필 사진: 선택 동의
   - 이메일: 선택 동의

### 2. 필요한 정보 수집

- **JavaScript 키** (Client ID)
- **REST API 키** (Client Secret 용도)
- **Admin 키** (선택사항)

## 🔧 GitHub 저장소 설정

### 1. 저장소 생성

```bash
# GitHub에서 새 저장소 생성 후
git clone https://github.com/your-username/compressor-ai-diagnosis.git
cd compressor-ai-diagnosis

# 프로젝트 파일 복사
# (현재 프로젝트의 모든 파일을 새 저장소로 복사)

git add .
git commit -m "Initial commit: 압축기 진단 시스템"
git push origin main
```

### 2. GitHub Secrets 설정

**Settings > Secrets and variables > Actions**에서 다음 변수들을 설정:

#### Repository Secrets
```
KAKAO_CLIENT_ID=your-javascript-key-here
KAKAO_CLIENT_SECRET=your-rest-api-key-here
SECRET_KEY=your-super-secret-jwt-key-here-change-this
```

#### Environment Variables (선택사항)
```
POSTGRES_USER=admin
POSTGRES_PASSWORD=secure-password-123
PRODUCTION_URL=https://your-domain.com
```

### 3. GitHub Container Registry 권한 설정

1. **Settings > Actions > General**
2. **Workflow permissions**에서 "Read and write permissions" 선택
3. "Allow GitHub Actions to create and approve pull requests" 체크

## 🐳 Docker 배포

### 로컬 테스트

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일 편집 (카카오톡 키 입력)
nano .env

# Docker Compose로 실행
docker-compose up -d

# 서비스 상태 확인
docker-compose ps
docker-compose logs compressor-diagnosis
```

### 접속 확인

- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **프론트엔드**: http://localhost:8501

## ☁️ 클라우드 배포

### GitHub Container Registry

```bash
# 자동 배포 (main 브랜치 푸시 시)
git push origin main

# 수동 배포
docker build -t ghcr.io/your-username/compressor-diagnosis:latest .
echo $GITHUB_TOKEN | docker login ghcr.io -u your-username --password-stdin
docker push ghcr.io/your-username/compressor-diagnosis:latest
```

### AWS 배포 (예시)

```bash
# AWS CLI 설정
aws configure

# ECR 저장소 생성
aws ecr create-repository --repository-name compressor-diagnosis

# 이미지 태깅 및 푸시
docker tag ghcr.io/your-username/compressor-diagnosis:latest \
  your-account.dkr.ecr.region.amazonaws.com/compressor-diagnosis:latest

aws ecr get-login-password --region region | \
  docker login --username AWS --password-stdin \
  your-account.dkr.ecr.region.amazonaws.com

docker push your-account.dkr.ecr.region.amazonaws.com/compressor-diagnosis:latest

# ECS 서비스 배포
aws ecs update-service --cluster your-cluster --service compressor-diagnosis --force-new-deployment
```

### Google Cloud Run 배포 (예시)

```bash
# gcloud CLI 설정
gcloud auth login
gcloud config set project your-project-id

# 이미지 태깅
docker tag ghcr.io/your-username/compressor-diagnosis:latest \
  gcr.io/your-project-id/compressor-diagnosis:latest

# 이미지 푸시
docker push gcr.io/your-project-id/compressor-diagnosis:latest

# Cloud Run 배포
gcloud run deploy compressor-diagnosis \
  --image gcr.io/your-project-id/compressor-diagnosis:latest \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars KAKAO_CLIENT_ID=$KAKAO_CLIENT_ID \
  --set-env-vars KAKAO_CLIENT_SECRET=$KAKAO_CLIENT_SECRET \
  --set-env-vars SECRET_KEY=$SECRET_KEY
```

## 🔒 보안 설정

### 1. HTTPS 설정 (프로덕션 필수)

```bash
# Let's Encrypt 인증서 (nginx 예시)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. 환경 변수 보안

```bash
# .env 파일 절대 Git에 커밋하지 않기
echo ".env" >> .gitignore

# 프로덕션에서는 시스템 환경 변수 사용
export KAKAO_CLIENT_ID="your-key"
export KAKAO_CLIENT_SECRET="your-secret"
export SECRET_KEY="your-jwt-secret"
```

### 3. 카카오톡 리다이렉트 URI 업데이트

프로덕션 배포 후 카카오 개발자 센터에서:
```
https://your-domain.com/auth/kakao/callback
```

## 📊 모니터링 설정

### 헬스체크 확인

```bash
# API 서버 상태 확인
curl http://your-domain.com:8000/

# 응답 예시
{"message":"압축기 진단 API 서버","version":"1.0.0"}
```

### 로그 모니터링

```bash
# Docker 로그 확인
docker logs compressor-diagnosis-compressor-diagnosis-1 --follow

# 시스템 로그 (Linux)
tail -f /var/log/syslog
```

## 🔄 업데이트 배포

### 자동 배포 (권장)

```bash
# 코드 변경 후
git add .
git commit -m "기능 개선: 새로운 진단 알고리즘 추가"
git push origin main

# GitHub Actions가 자동으로 빌드 및 배포
```

### 수동 배포

```bash
# 새 이미지 빌드
docker build -t ghcr.io/your-username/compressor-diagnosis:v2.0.0 .

# 푸시
docker push ghcr.io/your-username/compressor-diagnosis:v2.0.0

# 서비스 업데이트
docker-compose pull
docker-compose up -d
```

## 🚨 문제 해결

### 일반적인 문제들

1. **카카오톡 로그인 실패**
   ```bash
   # 설정 확인
   python kakao_config.py
   
   # 리다이렉트 URI 확인
   # 개발: http://localhost:8501/auth/kakao/callback
   # 프로덕션: https://your-domain.com/auth/kakao/callback
   ```

2. **Docker 이미지 빌드 실패**
   ```bash
   # 캐시 클리어 후 재빌드
   docker system prune -f
   docker build --no-cache -t compressor-diagnosis .
   ```

3. **데이터베이스 연결 오류**
   ```bash
   # 권한 확인
   ls -la compressor_system.db
   
   # 디렉토리 권한 설정
   chmod 755 ./
   chmod 644 compressor_system.db
   ```

### 로그 수집

```bash
# 모든 컨테이너 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs compressor-diagnosis

# 실시간 로그 추적
docker-compose logs -f compressor-diagnosis
```

## 📞 지원

문제가 지속되면:

1. GitHub Issues에 문제 보고
2. 로그 파일 첨부
3. 환경 정보 (OS, Docker 버전 등) 포함

## ✅ 배포 성공 확인

1. ✅ 웹사이트 접속 가능
2. ✅ 카카오톡 로그인 작동
3. ✅ 파일 업로드 및 진단 기능 정상
4. ✅ 관리자 포털 접근 가능
5. ✅ API 문서 접근 가능 (`/docs`)

---

🎉 배포 완료! 이제 사용자들이 압축기 진단 시스템을 사용할 수 있습니다.










