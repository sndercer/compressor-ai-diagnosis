# 🔧 압축기 진단 시스템

AI 기반 압축기 진단 시스템으로 카카오톡 로그인을 지원하는 웹 애플리케이션입니다.

## ✨ 주요 기능

- 🤖 **AI 기반 압축기 진단**: 머신러닝을 활용한 자동 진단 시스템
- 📱 **카카오톡 로그인**: 간편한 소셜 로그인 지원
- 📊 **실시간 대시보드**: 관리자용 모니터링 포털
- 🎵 **오디오 분석**: 압축기 소음 패턴 분석
- 📈 **진단 이력 관리**: 과거 진단 결과 추적 및 관리
- 🔒 **보안 인증**: JWT 토큰 기반 사용자 인증

## 🏗️ 시스템 아키텍처

```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ Database (SQLite)
                              ↓
                    AI Model (scikit-learn)
                              ↓
                    Kakao OAuth API
```

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/compressor-ai-diagnosis.git
cd compressor-ai-diagnosis
```

### 2. 환경 설정

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일을 편집하여 카카오톡 API 키 설정
# KAKAO_CLIENT_ID=your-kakao-javascript-key
# KAKAO_CLIENT_SECRET=your-kakao-rest-api-key
```

### 3. Docker로 실행

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 또는 Docker로 단독 실행
docker build -t compressor-diagnosis .
docker run -p 8000:8000 -p 8501:8501 --env-file .env compressor-diagnosis
```

### 4. 수동 설치 (개발용)

```bash
# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 백엔드 API 서버 시작
python backend_api.py

# 새 터미널에서 프론트엔드 시작
streamlit run admin_portal.py
```

## 🔧 카카오톡 로그인 설정

### 1. 카카오 개발자 센터 설정

1. [카카오 개발자 센터](https://developers.kakao.com/)에서 애플리케이션 생성
2. **플랫폼 설정**에서 웹 플랫폼 추가
3. **리다이렉트 URI** 설정: `http://localhost:8501/auth/kakao/callback`
4. **동의항목** 설정:
   - 닉네임 (profile_nickname) - 필수
   - 이메일 (account_email) - 선택

### 2. 환경 변수 설정

```bash
# .env 파일에 다음 내용 추가
KAKAO_CLIENT_ID=your-javascript-key
KAKAO_CLIENT_SECRET=your-rest-api-key
KAKAO_REDIRECT_URI=http://localhost:8501/auth/kakao/callback
```

### 3. 설정 확인

```bash
# 카카오톡 설정 상태 확인
python kakao_config.py
```

## 📦 API 엔드포인트

### 인증 관련
- `POST /auth/register` - 사용자 회원가입
- `POST /auth/login` - 이메일 로그인
- `GET /auth/kakao/login` - 카카오톡 로그인 URL 생성
- `GET /auth/kakao/callback` - 카카오톡 로그인 콜백
- `GET /users/me` - 현재 사용자 정보

### 진단 관련
- `POST /diagnosis/upload` - 파일 업로드 및 진단
- `GET /diagnosis/history` - 진단 이력 조회

### 관리자 관련
- `GET /customers` - 고객 목록 조회
- `GET /stats/system` - 시스템 통계

## 🌐 GitHub 배포

### 자동 배포 (GitHub Actions)

1. GitHub에 저장소 푸시
2. **Settings > Secrets and variables > Actions**에서 환경 변수 설정:
   ```
   KAKAO_CLIENT_ID
   KAKAO_CLIENT_SECRET
   SECRET_KEY
   ```
3. `main` 브랜치에 푸시하면 자동으로 배포됩니다.

### 수동 배포

```bash
# GitHub Container Registry에 이미지 푸시
docker build -t ghcr.io/your-username/compressor-diagnosis:latest .
docker push ghcr.io/your-username/compressor-diagnosis:latest

# 서버에서 실행
docker pull ghcr.io/your-username/compressor-diagnosis:latest
docker run -d -p 8000:8000 -p 8501:8501 --env-file .env \
  ghcr.io/your-username/compressor-diagnosis:latest
```

## 📁 프로젝트 구조

```
compressor-ai-diagnosis/
├── 📄 backend_api.py           # FastAPI 백엔드 서버
├── 📄 admin_portal.py          # Streamlit 관리자 포털
├── 📄 kakao_config.py          # 카카오톡 설정
├── 📄 requirements.txt         # Python 의존성
├── 📄 Dockerfile              # Docker 이미지 설정
├── 📄 docker-compose.yml       # Docker Compose 설정
├── 📄 start.sh                # 시작 스크립트
├── 📁 .github/workflows/       # GitHub Actions 워크플로우
├── 📁 uploads/                 # 업로드된 파일
├── 📁 models/                  # AI 모델 파일
├── 📁 backups/                 # 데이터베이스 백업
└── 📄 README.md               # 프로젝트 문서
```

## 🔍 사용법

### 1. 사용자 등록 및 로그인
- 이메일 회원가입 또는 카카오톡 로그인 사용
- JWT 토큰 기반 인증 시스템

### 2. 압축기 진단
1. 오디오 파일 업로드 (WAV, MP3 지원)
2. 장비 ID 입력
3. AI 자동 진단 실행
4. 결과 및 권장사항 확인

### 3. 관리자 기능
- 대시보드에서 시스템 상태 모니터링
- 고객 및 진단 이력 관리
- 데이터 백업 및 시스템 설정

## 🛠️ 기술 스택

- **Backend**: FastAPI, SQLite, PyJWT
- **Frontend**: Streamlit
- **AI/ML**: scikit-learn, librosa, numpy
- **Authentication**: Kakao OAuth 2.0
- **Deployment**: Docker, GitHub Actions
- **Database**: SQLite (개발), PostgreSQL (프로덕션)

## 📊 모니터링

- **헬스체크**: `/` 엔드포인트로 서비스 상태 확인
- **로그**: 애플리케이션 로그 모니터링
- **메트릭**: 진단 처리 시간, 정확도 추적

## 🔒 보안

- JWT 토큰 기반 인증
- 환경 변수로 민감 정보 관리
- CORS 설정으로 크로스 오리진 보안
- 파일 업로드 제한 및 검증

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

- 📧 Email: your-email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-username/compressor-ai-diagnosis/issues)

## 🎯 로드맵

- [ ] 웹 기반 프론트엔드 추가 (React/Vue.js)
- [ ] 실시간 알림 시스템
- [ ] 다국어 지원
- [ ] 모바일 앱 지원
- [ ] 고급 AI 모델 통합
- [ ] 클라우드 스토리지 연동

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!


