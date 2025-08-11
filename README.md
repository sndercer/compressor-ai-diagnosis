# 🏭 Compressor AI Diagnosis System

AI 기반 실시간 압축기 진단 시스템 - 산업용 유지보수를 위한 음향 분석 도구

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
# 방법 1: 직접 실행
streamlit run src/compressor_system.py

# 방법 2: 실행 스크립트 사용
cd src
python run_app.py
```

### 3. 웹 브라우저에서 접속
```
http://localhost:8501
```

## ✨ 주요 기능

### 🤖 AI 기반 진단
- **경량 AI 모델**: 노트북 환경에 최적화된 빠른 분석
- **MIMII 데이터셋 통합**: 산업용 기계 소음 데이터 활용
- **실시간 예측**: 업로드 즉시 진단 결과 제공

### 📊 실시간 분석
- **기본 분석**: 주파수, 진동, 노이즈 레벨 분석
- **고급 분석**: 스펙트럼, 멜-스펙트로그램 분석
- **시각화**: Plotly 기반 인터랙티브 차트

### 🎵 오디오 처리
- **다양한 형식 지원**: WAV, MP3 파일 처리
- **배치 처리**: 여러 파일 동시 업로드 및 분석
- **데이터 축소**: 대용량 오디오 데이터 효율적 처리

### 👥 협업 기능
- **고객 정보 관리**: 회사별 데이터 분류
- **라벨링 스튜디오**: 수동 데이터 라벨링 도구
- **AI 학습**: 사용자 데이터로 모델 개선

## 📁 프로젝트 구조

```
compressor-ai-diagnosis/
├── src/
│   ├── compressor_system.py      # 메인 애플리케이션
│   ├── config.py                 # 설정 파일
│   ├── mimii.py                  # MIMII 데이터 처리
│   ├── audio_data_reducer.py     # 오디오 데이터 축소
│   ├── test_system.py           # 시스템 테스트
│   └── run_app.py               # 실행 스크립트
├── models/                      # AI 모델 저장소
├── uploads/                     # 업로드된 파일
├── backups/                     # 데이터베이스 백업
└── requirements.txt             # Python 의존성
```

## 🔧 시스템 요구사항

### 필수 패키지
- Python 3.8+
- Streamlit 1.28.0+
- Librosa 0.10.0+
- Scikit-learn 1.1.0+
- Plotly 5.15.0+

### 권장 사양
- RAM: 8GB 이상
- 저장공간: 10GB 이상 (대용량 오디오 데이터 처리 시)
- CPU: 4코어 이상 (AI 모델 학습 시)

## 🎯 사용 시나리오

### 1. 압축기 정기 점검
- 정상 소리와 이상 소리 비교 분석
- 베어링 마모, 밸브 이상 등 진단
- 예방 정비 일정 수립

### 2. 고장 원인 분석
- 고장 발생 시점의 소리 데이터 분석
- 이상 패턴 식별 및 원인 추적
- 유사 사례와 비교 분석

### 3. AI 모델 학습
- 수집된 데이터로 모델 성능 향상
- 새로운 이상 패턴 학습
- 정확도 개선

## 🛠️ 문제 해결

### 🚨 주요 문제들

#### 1. 데이터베이스 데이터가 사라지는 문제
**증상**: 파일 업로드 후 재시작 시 데이터 사라짐

**해결 방법**:
1. **⚙️ 설정 탭** → **🗄️ 데이터베이스 관리** → **🔄 백업 생성**
2. **🔍 데이터 무결성 검증** 실행
3. 문제 시 **복구** 버튼 사용

#### 2. Streamlit 실행 오류
**증상**: `Fatal error in launcher: Unable to create process`

**해결 방법**:
```bash
# Streamlit 재설치
pip uninstall streamlit
pip install streamlit==1.28.0

# 대체 실행 방법
python -m streamlit run src/compressor_system.py
```

#### 3. 라이브러리 Import 오류
```bash
# 의존성 재설치
pip install -r requirements.txt

# 가상환경 사용 권장
python -m venv compressor_env
compressor_env\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 🔍 진단 도구

```bash
# 시스템 전체 테스트
cd src
python test_system.py

# 데이터베이스 진단
python check_database.py

# Streamlit 환경 진단
python fix_streamlit.py
```

### 📋 상세 문제 해결 가이드
자세한 문제 해결 방법은 [src/TROUBLESHOOTING.md](src/TROUBLESHOOTING.md)를 참조하세요.

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. GitHub Issues에 문제 등록
2. 시스템 로그 확인
3. 테스트 스크립트 실행

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**🏭 압축기 AI 진단 시스템으로 더 스마트한 유지보수를 시작하세요!**