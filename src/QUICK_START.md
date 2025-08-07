# ⚡ 빠른 시작 가이드

압축기 진단 시스템을 5분 안에 실행해보세요!

## 🎯 1단계: 카카오톡 개발자 센터 설정 (3분)

1. [카카오 개발자 센터](https://developers.kakao.com/) 접속
2. **내 애플리케이션 > 애플리케이션 추가하기**
3. **플랫폼 설정 > Web 플랫폼 추가**
4. **카카오 로그인 활성화**
5. **Redirect URI 추가**: `http://localhost:8501/auth/kakao/callback`
6. **앱 키** 메모:
   - JavaScript 키 (CLIENT_ID로 사용)
   - REST API 키 (CLIENT_SECRET으로 사용)

## 🔧 2단계: 환경 설정 (1분)

```bash
# 환경 변수 파일 생성
cp env.example .env
```

`.env` 파일을 편집하여 카카오톡 키 입력:
```env
KAKAO_CLIENT_ID=your-javascript-key-here
KAKAO_CLIENT_SECRET=your-rest-api-key-here
SECRET_KEY=your-super-secret-key-123
```

## 🚀 3단계: Docker로 실행 (1분)

```bash
# 전체 시스템 실행
docker-compose up -d

# 실행 상태 확인
docker-compose ps
```

## 🌐 4단계: 접속 확인

- **프론트엔드**: http://localhost:8501
- **백엔드 API**: http://localhost:8000  
- **API 문서**: http://localhost:8000/docs

## 🎉 완료!

이제 다음 기능들을 사용할 수 있습니다:
- ✅ 카카오톡 로그인
- ✅ 압축기 소음 파일 업로드
- ✅ AI 자동 진단
- ✅ 관리자 대시보드 (ID: admin, PW: admin123)

---

## 📱 GitHub 배포 (보너스)

### GitHub 저장소 생성
```bash
git init
git add .
git commit -m "압축기 진단 시스템 초기 커밋"
git remote add origin https://github.com/your-username/compressor-diagnosis.git
git push -u origin main
```

### GitHub Secrets 설정
**Settings > Secrets and variables > Actions**에서:
- `KAKAO_CLIENT_ID`: 카카오 JavaScript 키
- `KAKAO_CLIENT_SECRET`: 카카오 REST API 키  
- `SECRET_KEY`: JWT 암호화 키

### 자동 배포
`main` 브랜치에 푸시하면 GitHub Actions가 자동으로:
1. 코드 품질 검사
2. Docker 이미지 빌드
3. GitHub Container Registry에 배포
4. 클라우드 서비스 배포 (설정 시)

---

## 🆘 문제 해결

### 카카오톡 로그인 오류
```bash
# 설정 확인
python kakao_config.py
```

### 서비스 상태 확인
```bash
# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart
```

### 포트 충돌
`.env` 파일에서 포트 변경:
```env
API_PORT=8000
STREAMLIT_PORT=8501
```

---

🎊 **축하합니다!** 압축기 진단 시스템이 성공적으로 실행되었습니다!


