# run_integrated_system.py - 통합 시스템 실행 스크립트
"""
AI 압축기 진단 통합 시스템 실행기

이 스크립트는 다음 기능을 제공합니다:
1. 통합 웹 애플리케이션 실행
2. 데이터베이스 초기화
3. 샘플 데이터 생성 (선택사항)
4. 시스템 상태 체크
"""

import os
import sys
import subprocess
import sqlite3
import json
from datetime import datetime, timedelta
import streamlit as st

def check_dependencies():
    """필수 의존성 확인"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'scikit-learn', 
        'librosa', 'plotly', 'audio_recorder_streamlit'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지가 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n설치 명령어:")
        print("pip install -r requirements_integrated.txt")
        return False
    
    print("✅ 모든 필수 패키지가 설치되어 있습니다.")
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        'models',
        'field_recordings', 
        'uploads',
        'reports',
        'backups'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 디렉토리 생성: {directory}")

def initialize_database():
    """데이터베이스 초기화"""
    try:
        from main_integrated_app import IntegratedDiagnosisSystem
        
        print("🗄️ 데이터베이스 초기화 중...")
        system = IntegratedDiagnosisSystem()
        print("✅ 데이터베이스 초기화 완료")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        return False

def create_sample_data():
    """샘플 데이터 생성 (선택사항)"""
    try:
        conn = sqlite3.connect('integrated_diagnosis_system.db')
        cursor = conn.cursor()
        
        # 샘플 진단 데이터
        sample_diagnoses = [
            ('삼성전자', '냉동고', 'REF-001', '1층 주방', '김기술', '이상 소음', 
             '압축기 베어링 마모', 0.87, '위험', 'correct'),
            ('LG유통', '에어컨', 'AC-002', '2층 사무실', '이엔지', '진동', 
             '팬 불균형', 0.82, '경고', 'correct'),
            ('현대마트', '냉동고', 'REF-003', '지하 창고', '박현장', '없음', 
             '정상 압축기', 0.94, '정상', 'correct'),
        ]
        
        for data in sample_diagnoses:
            cursor.execute('''
                INSERT INTO field_diagnoses (
                    customer_name, equipment_type, equipment_id, location,
                    technician_name, suspected_issue, ai_diagnosis, ai_confidence,
                    ai_severity, field_verification, status, labeling_approved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'training_ready', 1)
            ''', data)
        
        # 샘플 일별 성능 데이터
        today = datetime.now().date()
        for i in range(7):
            date = today - timedelta(days=i)
            cursor.execute('''
                INSERT OR IGNORE INTO daily_performance (
                    date, total_diagnoses, correct_diagnoses, accuracy, model_version
                ) VALUES (?, ?, ?, ?, ?)
            ''', (date, 10 + i, 8 + i, (8 + i) / (10 + i), 'v1.0.0'))
        
        conn.commit()
        conn.close()
        
        print("✅ 샘플 데이터 생성 완료")
        return True
        
    except Exception as e:
        print(f"❌ 샘플 데이터 생성 실패: {e}")
        return False

def check_system_status():
    """시스템 상태 체크"""
    print("\n🔍 시스템 상태 확인...")
    
    # 데이터베이스 연결 체크
    try:
        conn = sqlite3.connect('integrated_diagnosis_system.db')
        cursor = conn.cursor()
        
        # 테이블 존재 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        expected_tables = ['field_diagnoses', 'model_training_history', 
                          'daily_performance', 'user_activity_log']
        
        existing_tables = [table[0] for table in tables]
        
        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✅ 테이블 {table} 존재")
            else:
                print(f"   ❌ 테이블 {table} 없음")
        
        # 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) FROM field_diagnoses")
        diagnosis_count = cursor.fetchone()[0]
        print(f"   📊 진단 데이터: {diagnosis_count}건")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 데이터베이스 체크 실패: {e}")
    
    # 디렉토리 존재 확인
    directories = ['models', 'field_recordings', 'uploads']
    for directory in directories:
        if os.path.exists(directory):
            print(f"   ✅ 디렉토리 {directory} 존재")
        else:
            print(f"   ❌ 디렉토리 {directory} 없음")

def run_system():
    """시스템 실행"""
    print("🚀 AI 압축기 진단 통합 시스템을 시작합니다...")
    
    try:
        # Streamlit 앱 실행
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "main_integrated_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        print(f"🌐 웹 애플리케이션을 시작합니다...")
        print(f"📱 브라우저에서 http://localhost:8501 에 접속하세요")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 시스템이 중단되었습니다.")
    except Exception as e:
        print(f"❌ 시스템 실행 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("🏭 AI 압축기 진단 통합 시스템")
    print("=" * 60)
    
    # 1. 의존성 확인
    if not check_dependencies():
        print("\n❌ 의존성 확인 실패. 프로그램을 종료합니다.")
        return
    
    # 2. 디렉토리 생성
    create_directories()
    
    # 3. 데이터베이스 초기화
    if not initialize_database():
        print("\n❌ 데이터베이스 초기화 실패. 프로그램을 종료합니다.")
        return
    
    # 4. 선택사항: 샘플 데이터 생성
    choice = input("\n📊 샘플 데이터를 생성하시겠습니까? (y/n): ").lower()
    if choice in ['y', 'yes', '예']:
        create_sample_data()
    
    # 5. 시스템 상태 체크
    check_system_status()
    
    # 6. 시스템 실행
    choice = input("\n🚀 시스템을 시작하시겠습니까? (y/n): ").lower()
    if choice in ['y', 'yes', '예']:
        run_system()
    else:
        print("👋 시스템 설정이 완료되었습니다. 언제든지 다시 실행하세요!")

if __name__ == "__main__":
    main()
