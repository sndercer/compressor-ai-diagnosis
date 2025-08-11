# 📁 폴더 구조 재정리 계획

## 🎯 목표
현재 `src/` 폴더에 모든 파일이 섞여 있는 상태를 기능별로 정리하여 가독성과 유지보수성을 향상시킵니다.

## 📂 제안하는 새로운 구조

```
compressor-ai-diagnosis/
├── 📱 apps/                          # Frontend Applications
│   ├── field_diagnosis_app.py         # 메인 현장 진단 앱
│   └── admin_portal.py               # 관리자 포털
│
├── 🔌 api/                           # Backend Services
│   ├── backend_api.py                # FastAPI 백엔드
│   ├── compressor_system.py          # AI 진단 엔진
│   └── notification_service.py       # 알림 서비스
│
├── 📄 reports/                       # Report Generation
│   ├── reliable_report_generator.py  # 메인 리포트 생성기
│   ├── pdf_report_generator.py       # PDF 생성기
│   └── simple_pdf_generator.py       # 간단 PDF 생성기
│
├── ⚙️ config/                        # Configuration
│   ├── config.py                     # 시스템 설정
│   ├── kakao_config.py              # OAuth 설정
│   └── env.example                   # 환경변수 예시
│
├── 🚀 scripts/                       # Deployment Scripts
│   ├── run_all_services.py          # 전체 서비스 실행
│   ├── start_backend.py             # 백엔드 시작
│   ├── start_field_app.py           # 현장 앱 시작
│   ├── deploy.sh                    # 배포 스크립트
│   └── start.sh                     # 시스템 시작
│
├── 📚 docs/                          # Documentation
│   ├── README.md                     # 메인 문서
│   ├── ARCHITECTURE.md               # 아키텍처 문서
│   ├── DEPLOYMENT_GUIDE.md           # 배포 가이드
│   ├── QUICK_START.md                # 빠른 시작
│   └── mobile_deployment_guide.md    # 모바일 배포
│
├── 💾 data/                          # Data Storage
│   ├── uploads/                      # 업로드 파일
│   ├── field_uploads/                # 현장 진단 파일
│   ├── reports_generated/            # 생성된 리포트
│   ├── models/                       # AI 모델
│   ├── backups/                      # 백업
│   └── fonts/                        # 폰트 파일
│
├── 🗃️ database/                      # Database Files
│   ├── field_diagnosis.db           # 현장 진단 DB
│   ├── compressor_system.db         # 시스템 DB
│   └── standalone_compressor.db     # 독립 실행 DB
│
├── 📦 requirements/                  # Dependencies
│   ├── requirements.txt             # 로컬 개발용
│   ├── requirements_cloud.txt       # 클라우드 배포용
│   └── requirements_dev.txt         # 개발 도구용
│
├── 🔧 utils/                         # Utility Functions
│   ├── audio_processing.py          # 오디오 처리 유틸
│   ├── database_utils.py            # DB 유틸리티
│   └── file_utils.py                # 파일 처리 유틸
│
└── 📋 tests/                         # Test Files (나중에 추가)
    ├── test_api.py                   # API 테스트
    ├── test_ai_engine.py             # AI 엔진 테스트
    └── test_reports.py               # 리포트 테스트
```

## 🔄 마이그레이션 단계

### 1단계: 폴더 생성
```bash
mkdir apps api reports config scripts docs data database requirements utils
```

### 2단계: 파일 이동
```bash
# Frontend apps
mv field_diagnosis_app.py apps/
mv admin_portal.py apps/

# Backend services  
mv backend_api.py api/
mv compressor_system.py api/
mv notification_service.py api/

# Report generators
mv reliable_report_generator.py reports/
mv pdf_report_generator.py reports/
mv simple_pdf_generator.py reports/

# Configuration
mv config.py config/
mv kakao_config.py config/
mv env.example config/

# Scripts
mv run_all_services.py scripts/
mv start_*.py scripts/
mv deploy.sh scripts/
mv start.sh scripts/

# Documentation
mv *.md docs/
mv mobile_deployment_guide.md docs/

# Data storage
mv uploads/ data/
mv field_uploads/ data/
mv reports/ data/reports_generated/
mv models/ data/
mv backups/ data/
mv fonts/ data/

# Database
mv *.db database/

# Requirements
mv requirements*.txt requirements/
```

### 3단계: Import 경로 수정
모든 Python 파일에서 import 경로를 새로운 구조에 맞게 수정

### 4단계: 설정 파일 업데이트
- Dockerfile, docker-compose.yml 경로 수정
- 배포 스크립트 경로 수정
- README.md 업데이트

## 🎯 장점

1. **🔍 가독성 향상**: 기능별로 명확히 분리
2. **🛠️ 유지보수 용이**: 관련 파일들이 함께 그룹화
3. **👥 협업 효율성**: 팀원들이 파일 찾기 쉬움
4. **📈 확장성**: 새로운 기능 추가 시 적절한 위치에 배치
5. **🧪 테스트 관리**: 테스트 파일 별도 관리
6. **📦 배포 최적화**: 배포 시 필요한 파일만 선택적 포함

## ⚠️ 주의사항

1. **Import 경로**: 모든 상대 import를 절대 import로 변경
2. **설정 파일**: 경로 하드코딩된 부분 모두 수정
3. **배포 스크립트**: Dockerfile, 배포 스크립트 경로 수정
4. **Git 이력**: `git mv` 사용으로 파일 이력 보존

## 🚀 실행 계획

이 재구성을 원하시면 단계별로 진행하겠습니다:

1. **1차**: 폴더 생성 및 주요 파일 이동
2. **2차**: Import 경로 수정 및 테스트
3. **3차**: 설정 파일 및 문서 업데이트
4. **4차**: 배포 테스트 및 최종 검증

재구성을 진행할까요? 🤔
