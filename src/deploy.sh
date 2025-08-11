#!/bin/bash

# 압축기 진단 시스템 - 배포 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 압축기 진단 시스템 배포를 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 확인
check_requirements() {
    print_status "시스템 요구사항을 확인합니다..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        print_error "Docker가 설치되지 않았습니다. https://docs.docker.com/get-docker/ 에서 설치해주세요."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    print_status "✅ 시스템 요구사항 확인 완료"
}

# 환경 변수 파일 확인
check_env_file() {
    print_status "환경 변수 파일을 확인합니다..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env 파일이 없습니다. env.example을 복사합니다..."
        cp env.example .env
        print_warning "⚠️ .env 파일을 편집하여 카카오톡 API 키를 설정해주세요."
        print_warning "필수 설정: KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET"
        
        # 사용자에게 설정 확인
        read -p "환경 변수를 설정하셨나요? (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            print_error "환경 변수 설정 후 다시 실행해주세요."
            exit 1
        fi
    fi
    
    print_status "✅ 환경 변수 파일 확인 완료"
}

# 카카오톡 설정 확인
check_kakao_config() {
    print_status "카카오톡 설정을 확인합니다..."
    
    if python3 kakao_config.py | grep -q "❌ 설정 필요"; then
        print_warning "카카오톡 설정이 완료되지 않았습니다."
        print_warning "다음 가이드를 참조하여 설정해주세요:"
        print_warning "https://developers.kakao.com/"
        
        read -p "카카오톡 설정을 완료하셨나요? (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            print_error "카카오톡 설정 완료 후 다시 실행해주세요."
            exit 1
        fi
    fi
    
    print_status "✅ 카카오톡 설정 확인 완료"
}

# Docker 이미지 빌드
build_image() {
    print_status "Docker 이미지를 빌드합니다..."
    
    docker build -t compressor-diagnosis:latest . || {
        print_error "Docker 이미지 빌드에 실패했습니다."
        exit 1
    }
    
    print_status "✅ Docker 이미지 빌드 완료"
}

# 기존 컨테이너 정리
cleanup_containers() {
    print_status "기존 컨테이너를 정리합니다..."
    
    docker-compose down --remove-orphans 2>/dev/null || true
    
    print_status "✅ 컨테이너 정리 완료"
}

# 서비스 시작
start_services() {
    print_status "서비스를 시작합니다..."
    
    docker-compose up -d || {
        print_error "서비스 시작에 실패했습니다."
        print_error "로그를 확인해주세요: docker-compose logs"
        exit 1
    }
    
    print_status "✅ 서비스 시작 완료"
}

# 서비스 상태 확인
check_services() {
    print_status "서비스 상태를 확인합니다..."
    
    sleep 10  # 서비스 시작 대기
    
    # API 서버 확인
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        print_status "✅ 백엔드 API 서버가 정상 실행 중입니다."
    else
        print_warning "⚠️ 백엔드 API 서버 접속에 실패했습니다."
    fi
    
    # Streamlit 확인
    if curl -f http://localhost:8501/ >/dev/null 2>&1; then
        print_status "✅ Streamlit 프론트엔드가 정상 실행 중입니다."
    else
        print_warning "⚠️ Streamlit 프론트엔드 접속에 실패했습니다."
    fi
    
    # 컨테이너 상태 출력
    print_status "컨테이너 상태:"
    docker-compose ps
}

# 배포 정보 출력
show_deployment_info() {
    echo ""
    echo "🎉 배포가 완료되었습니다!"
    echo ""
    echo "📡 서비스 접속 정보:"
    echo "  • 백엔드 API: http://localhost:8000"
    echo "  • API 문서: http://localhost:8000/docs"
    echo "  • 프론트엔드: http://localhost:8501"
    echo ""
    echo "🔧 유용한 명령어:"
    echo "  • 로그 확인: docker-compose logs -f"
    echo "  • 서비스 중지: docker-compose down"
    echo "  • 서비스 재시작: docker-compose restart"
    echo ""
    echo "📝 관리자 로그인 정보:"
    echo "  • ID: admin"
    echo "  • 비밀번호: admin123"
    echo ""
}

# GitHub 배포 가이드
show_github_guide() {
    echo "🔗 GitHub 배포 가이드:"
    echo ""
    echo "1. GitHub 저장소 생성 후 코드 푸시:"
    echo "   git add ."
    echo "   git commit -m 'Initial commit: 압축기 진단 시스템'"
    echo "   git push origin main"
    echo ""
    echo "2. GitHub Secrets 설정 (Settings > Secrets and variables > Actions):"
    echo "   • KAKAO_CLIENT_ID"
    echo "   • KAKAO_CLIENT_SECRET"
    echo "   • SECRET_KEY"
    echo ""
    echo "3. main 브랜치에 푸시하면 자동 배포됩니다!"
    echo ""
    echo "📖 자세한 내용은 DEPLOYMENT_GUIDE.md를 참조하세요."
}

# 메인 실행
main() {
    echo "================================================="
    echo "🔧 압축기 진단 시스템 배포 스크립트"
    echo "================================================="
    
    check_requirements
    check_env_file
    check_kakao_config
    build_image
    cleanup_containers
    start_services
    check_services
    show_deployment_info
    show_github_guide
    
    echo ""
    echo "✅ 모든 배포 과정이 완료되었습니다!"
}

# 스크립트 인수 처리
case "${1:-}" in
    --check-only)
        check_requirements
        check_env_file
        check_kakao_config
        ;;
    --build-only)
        build_image
        ;;
    --restart)
        cleanup_containers
        start_services
        check_services
        ;;
    --help|-h)
        echo "사용법: $0 [옵션]"
        echo ""
        echo "옵션:"
        echo "  --check-only    요구사항과 설정만 확인"
        echo "  --build-only    Docker 이미지만 빌드"
        echo "  --restart       서비스 재시작"
        echo "  --help, -h      이 도움말 표시"
        echo ""
        ;;
    *)
        main
        ;;
esac



# 압축기 진단 시스템 - 배포 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 압축기 진단 시스템 배포를 시작합니다..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 확인
check_requirements() {
    print_status "시스템 요구사항을 확인합니다..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        print_error "Docker가 설치되지 않았습니다. https://docs.docker.com/get-docker/ 에서 설치해주세요."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    print_status "✅ 시스템 요구사항 확인 완료"
}

# 환경 변수 파일 확인
check_env_file() {
    print_status "환경 변수 파일을 확인합니다..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env 파일이 없습니다. env.example을 복사합니다..."
        cp env.example .env
        print_warning "⚠️ .env 파일을 편집하여 카카오톡 API 키를 설정해주세요."
        print_warning "필수 설정: KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET"
        
        # 사용자에게 설정 확인
        read -p "환경 변수를 설정하셨나요? (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            print_error "환경 변수 설정 후 다시 실행해주세요."
            exit 1
        fi
    fi
    
    print_status "✅ 환경 변수 파일 확인 완료"
}

# 카카오톡 설정 확인
check_kakao_config() {
    print_status "카카오톡 설정을 확인합니다..."
    
    if python3 kakao_config.py | grep -q "❌ 설정 필요"; then
        print_warning "카카오톡 설정이 완료되지 않았습니다."
        print_warning "다음 가이드를 참조하여 설정해주세요:"
        print_warning "https://developers.kakao.com/"
        
        read -p "카카오톡 설정을 완료하셨나요? (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            print_error "카카오톡 설정 완료 후 다시 실행해주세요."
            exit 1
        fi
    fi
    
    print_status "✅ 카카오톡 설정 확인 완료"
}

# Docker 이미지 빌드
build_image() {
    print_status "Docker 이미지를 빌드합니다..."
    
    docker build -t compressor-diagnosis:latest . || {
        print_error "Docker 이미지 빌드에 실패했습니다."
        exit 1
    }
    
    print_status "✅ Docker 이미지 빌드 완료"
}

# 기존 컨테이너 정리
cleanup_containers() {
    print_status "기존 컨테이너를 정리합니다..."
    
    docker-compose down --remove-orphans 2>/dev/null || true
    
    print_status "✅ 컨테이너 정리 완료"
}

# 서비스 시작
start_services() {
    print_status "서비스를 시작합니다..."
    
    docker-compose up -d || {
        print_error "서비스 시작에 실패했습니다."
        print_error "로그를 확인해주세요: docker-compose logs"
        exit 1
    }
    
    print_status "✅ 서비스 시작 완료"
}

# 서비스 상태 확인
check_services() {
    print_status "서비스 상태를 확인합니다..."
    
    sleep 10  # 서비스 시작 대기
    
    # API 서버 확인
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        print_status "✅ 백엔드 API 서버가 정상 실행 중입니다."
    else
        print_warning "⚠️ 백엔드 API 서버 접속에 실패했습니다."
    fi
    
    # Streamlit 확인
    if curl -f http://localhost:8501/ >/dev/null 2>&1; then
        print_status "✅ Streamlit 프론트엔드가 정상 실행 중입니다."
    else
        print_warning "⚠️ Streamlit 프론트엔드 접속에 실패했습니다."
    fi
    
    # 컨테이너 상태 출력
    print_status "컨테이너 상태:"
    docker-compose ps
}

# 배포 정보 출력
show_deployment_info() {
    echo ""
    echo "🎉 배포가 완료되었습니다!"
    echo ""
    echo "📡 서비스 접속 정보:"
    echo "  • 백엔드 API: http://localhost:8000"
    echo "  • API 문서: http://localhost:8000/docs"
    echo "  • 프론트엔드: http://localhost:8501"
    echo ""
    echo "🔧 유용한 명령어:"
    echo "  • 로그 확인: docker-compose logs -f"
    echo "  • 서비스 중지: docker-compose down"
    echo "  • 서비스 재시작: docker-compose restart"
    echo ""
    echo "📝 관리자 로그인 정보:"
    echo "  • ID: admin"
    echo "  • 비밀번호: admin123"
    echo ""
}

# GitHub 배포 가이드
show_github_guide() {
    echo "🔗 GitHub 배포 가이드:"
    echo ""
    echo "1. GitHub 저장소 생성 후 코드 푸시:"
    echo "   git add ."
    echo "   git commit -m 'Initial commit: 압축기 진단 시스템'"
    echo "   git push origin main"
    echo ""
    echo "2. GitHub Secrets 설정 (Settings > Secrets and variables > Actions):"
    echo "   • KAKAO_CLIENT_ID"
    echo "   • KAKAO_CLIENT_SECRET"
    echo "   • SECRET_KEY"
    echo ""
    echo "3. main 브랜치에 푸시하면 자동 배포됩니다!"
    echo ""
    echo "📖 자세한 내용은 DEPLOYMENT_GUIDE.md를 참조하세요."
}

# 메인 실행
main() {
    echo "================================================="
    echo "🔧 압축기 진단 시스템 배포 스크립트"
    echo "================================================="
    
    check_requirements
    check_env_file
    check_kakao_config
    build_image
    cleanup_containers
    start_services
    check_services
    show_deployment_info
    show_github_guide
    
    echo ""
    echo "✅ 모든 배포 과정이 완료되었습니다!"
}

# 스크립트 인수 처리
case "${1:-}" in
    --check-only)
        check_requirements
        check_env_file
        check_kakao_config
        ;;
    --build-only)
        build_image
        ;;
    --restart)
        cleanup_containers
        start_services
        check_services
        ;;
    --help|-h)
        echo "사용법: $0 [옵션]"
        echo ""
        echo "옵션:"
        echo "  --check-only    요구사항과 설정만 확인"
        echo "  --build-only    Docker 이미지만 빌드"
        echo "  --restart       서비스 재시작"
        echo "  --help, -h      이 도움말 표시"
        echo ""
        ;;
    *)
        main
        ;;
esac










