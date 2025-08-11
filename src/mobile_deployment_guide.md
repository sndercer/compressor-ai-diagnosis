# 📱 현장 진단 앱 모바일 배포 가이드

## 🚀 빠른 시작 (로컬 네트워크)

### 1단계: PC에서 네트워크 모드 실행
```bash
# 현재 디렉토리에서 실행
streamlit run field_diagnosis_app.py --server.address 0.0.0.0 --server.port 8501
```

### 2단계: PC IP 주소 확인
```bash
# Windows
ipconfig

# 192.168.x.x 형태의 IP 주소 확인
```

### 3단계: 모바일에서 접속
- 같은 Wi-Fi에 연결
- 브라우저에서 `http://[PC_IP]:8501` 접속
- 예: `http://192.168.1.100:8501`

---

## 🔒 전문적 배포 (클라우드)

### Option A: AWS/Google Cloud
```bash
# 클라우드 서버에 배포
sudo ufw allow 8501
streamlit run field_diagnosis_app.py --server.address 0.0.0.0
```

### Option B: ngrok (임시 터널)
```bash
# ngrok 설치 후
ngrok http 8501
# https://xyz.ngrok.io 주소로 어디서든 접속 가능
```

---

## 📱 모바일 최적화 체크리스트

### ✅ 현재 구현된 기능
- [x] 모바일 반응형 CSS
- [x] 큰 터치 버튼
- [x] 음성 녹음 지원
- [x] 오프라인 모드
- [x] 로컬 데이터 저장 (SQLite)
- [x] HTML/텍스트 리포트 생성

### 🔄 추가 고려사항
- [ ] HTTPS 설정 (보안)
- [ ] PWA (앱처럼 설치)
- [ ] 데이터 동기화
- [ ] 기술자별 계정 관리
- [ ] GPS 위치 기록

---

## 🛠️ 현장 사용 팁

### 인터넷 연결이 없는 경우
- ✅ 오프라인 모드 자동 전환
- ✅ 로컬 SQLite 데이터베이스 사용
- ✅ HTML/텍스트 리포트 생성 가능

### 음성 녹음 권한
- 브라우저에서 마이크 권한 허용 필요
- HTTPS 환경에서 더 안정적

### 데이터 백업
```bash
# 진단 데이터 백업
cp field_diagnosis.db backup_$(date +%Y%m%d).db
```

---

## 🎯 즉시 사용 가능!

현재 상태에서도 충분히 현장에서 사용 가능합니다:

1. **PC와 스마트폰이 같은 Wi-Fi에 연결**
2. **PC에서 앱 실행** (네트워크 모드)
3. **스마트폰 브라우저로 접속**
4. **바로 고객 현장에서 진단 시작!**

추가 기능은 필요에 따라 점진적으로 개발하면 됩니다.
