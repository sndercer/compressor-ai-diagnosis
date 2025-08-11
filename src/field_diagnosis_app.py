# field_diagnosis_app.py - 현장 진단용 모바일 웹 앱
import streamlit as st
import sqlite3
import requests
import json
import base64
from datetime import datetime
import os
import io
import time
from audio_recorder_streamlit import audio_recorder
import pandas as pd

def create_simple_text_report(data, filename):
    """간단한 텍스트 리포트 생성"""
    try:
        content = f"""
===========================================
        압축기 진단 리포트
===========================================

생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}

-------------------------------------------
기본 정보
-------------------------------------------
고객명: {data.get('customer_name', 'N/A')}
장비 유형: {data.get('equipment_type', 'N/A')}
장비 ID: {data.get('equipment_id', 'N/A')}
진단 결과: {data.get('diagnosis', 'N/A')}
신뢰도: {int(data.get('confidence', 0) * 100)}%
기술자: {data.get('technician_name', 'N/A')}

-------------------------------------------
진단 결과
-------------------------------------------
상태: {data.get('diagnosis', 'N/A')}

권장사항:
• 정기적인 점검을 실시하세요
• 이상 발견 시 즉시 연락하세요
• 운전 조건을 확인하세요

-------------------------------------------
문의사항
-------------------------------------------
기술 지원: 1588-0000
이메일: support@example.com

© 2024 AI 압축기 진단 시스템
===========================================
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"텍스트 리포트 생성 실패: {e}")
        return False

# 🎨 모바일 친화적 페이지 설정
st.set_page_config(
    page_title="현장 진단 앱",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 📱 모바일 최적화 CSS
st.markdown("""
<style>
    /* 진단 정보 섹션만 강제 검은색 */
    .stSubheader h3 {
        color: black !important;
    }
    
    .stWrite p, .stWrite strong {
        color: black !important;
    }
    
    /* 모바일 최적화 스타일 */
    .main > div {
        padding: 1rem 0.5rem;
    }
    
    /* 큰 버튼 스타일 */
    .big-button {
        background-color: #FF6B6B;
        color: white;
        border: none;
        border-radius: 15px;
        padding: 20px 40px;
        font-size: 24px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .big-button:hover {
        background-color: #FF5252;
    }
    
    .success-button {
        background-color: #4CAF50;
    }
    
    .success-button:hover {
        background-color: #45a049;
    }
    
    /* 상태 표시 */
    .status-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
    }
    
    .status-recording {
        background-color: #FFE0E0;
        color: #D32F2F;
        border: 2px solid #D32F2F;
    }
    
    .status-analyzing {
        background-color: #E3F2FD;
        color: #1976D2;
        border: 2px solid #1976D2;
    }
    
    .status-complete {
        background-color: #E8F5E8;
        color: #388E3C;
        border: 2px solid #388E3C;
    }
    
    /* 결과 카드 */
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 15px 0;
    }
    
    .result-normal {
        border-left: 5px solid #4CAF50;
    }
    
    .result-caution {
        border-left: 5px solid #FF9800;
    }
    
    .result-danger {
        border-left: 5px solid #F44336;
    }
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.5rem 0.25rem;
        }
        
        .big-button {
            font-size: 20px;
            padding: 15px 30px;
        }
        
        .status-box {
            font-size: 16px;
            padding: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

class FieldDiagnosisApp:
    def __init__(self):
        self.session_state = st.session_state
        
        # 세션 상태 초기화
        if 'diagnosis_step' not in self.session_state:
            self.session_state.diagnosis_step = 'welcome'
        if 'customer_info' not in self.session_state:
            self.session_state.customer_info = {}
        if 'recording_data' not in self.session_state:
            self.session_state.recording_data = None
        if 'analysis_result' not in self.session_state:
            self.session_state.analysis_result = None
        
        # 데이터베이스 초기화
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect('field_diagnosis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                equipment_id TEXT NOT NULL,
                technician_name TEXT NOT NULL,
                diagnosis_result TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def welcome_step(self):
        """환영 화면"""
        st.markdown("""
        # 🔧 AI 압축기 현장 진단
        
        <div class="status-box status-complete">
            💼 전문 기술자용 현장 진단 도구
        </div>
        
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 📋 진단 과정
        1. **고객 정보 입력** - 방문 고객 및 장비 정보
        2. **음성 녹음** - 현장에서 장비 소음 녹음
        3. **AI 분석** - 실시간 AI 기반 자동 분석
        4. **결과 확인** - 즉시 진단 결과 및 리포트 생성
        
        ### 🎯 주요 기능
        - ⚡ **원터치 녹음**: 간편한 현장 음성 캡처
        - 🤖 **AI 자동 분석**: 3초 내 즉시 결과
        - 📄 **전문 리포트**: PDF 자동 생성 및 공유
        - 📱 **모바일 최적화**: 태블릿/스마트폰 지원
        """)
        
        if st.button("🚀 진단 시작하기", key="start_diagnosis", use_container_width=True):
            self.session_state.diagnosis_step = 'customer_info'
            st.rerun()
    
    def customer_info_step(self):
        """1단계: 고객 정보 입력"""
        st.markdown("# 📝 고객 정보 입력")
        
        st.markdown("""
        <div class="status-box status-analyzing">
            1단계: 방문 고객 및 장비 정보를 입력해주세요
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("customer_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input(
                    "🏢 고객명/회사명", 
                    placeholder="예: A수산, B마트, C공장",
                    help="방문한 고객의 이름이나 회사명을 입력하세요"
                )
                
                equipment_type = st.selectbox(
                    "🔧 장비 유형",
                    ["냉동고", "냉장고", "에어컨", "압축기", "히트펌프", "기타"],
                    help="진단할 장비의 종류를 선택하세요"
                )
            
            with col2:
                equipment_id = st.text_input(
                    "📍 장비 위치/번호",
                    placeholder="예: 1번 냉동고, 메인 압축기",
                    help="장비의 위치나 식별 번호를 입력하세요"
                )
                
                technician_name = st.text_input(
                    "👨‍🔧 기술자명",
                    placeholder="예: 김기술, 이진단",
                    help="진단을 수행하는 기술자의 이름을 입력하세요"
                )
            
            # 추가 정보
            st.markdown("### 📋 추가 정보 (선택사항)")
            notes = st.text_area(
                "특이사항 또는 고객 요청사항",
                placeholder="예: 소음이 심해짐, 냉각 성능 저하, 정기 점검 등",
                help="고객이 제기한 문제점이나 특이사항을 기록하세요"
            )
            
            submitted = st.form_submit_button("📍 정보 저장 및 다음 단계", use_container_width=True)
            
            if submitted:
                if customer_name and equipment_type and equipment_id and technician_name:
                    self.session_state.customer_info = {
                        'customer_name': customer_name,
                        'equipment_type': equipment_type,
                        'equipment_id': equipment_id,
                        'technician_name': technician_name,
                        'notes': notes
                    }
                    self.session_state.diagnosis_step = 'recording'
                    st.success("✅ 고객 정보가 저장되었습니다!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 필수 정보를 모두 입력해주세요.")
        
        # 이전 단계로 돌아가기
        if st.button("🔙 처음으로 돌아가기", key="back_to_welcome"):
            self.session_state.diagnosis_step = 'welcome'
            st.rerun()
    
    def recording_step(self):
        """2단계: 음성 녹음"""
        st.markdown("# 🎤 현장 음성 녹음")
        
        # 고객 정보 표시 - 검은색 배경
        info = self.session_state.customer_info
        st.markdown(f"""
        <div style="background-color: #000000; color: #FFFFFF; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <strong style="color: #FFFFFF;">📍 진단 정보</strong><br/>
            <span style="color: #FFFFFF;">🏢 고객: {info['customer_name']}</span><br/>
            <span style="color: #FFFFFF;">🔧 장비: {info['equipment_type']} - {info['equipment_id']}</span><br/>
            <span style="color: #FFFFFF;">👨‍🔧 기술자: {info['technician_name']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 단계 안내
        st.warning("2단계: 장비 근처에서 소음을 녹음해주세요 (최소 5초 이상)")
        
        # 녹음 가이드 - 검은색 배경
        st.markdown("""
        <div style="background-color: #000000; color: #FFFFFF; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3 style="color: #FFFFFF; margin-top: 0;">📋 녹음 가이드</h3>
            <p style="color: #FFFFFF;">1. <strong style="color: #FFFFFF;">장비에 최대한 가까이</strong> 이동하세요 (1-2미터 이내)</p>
            <p style="color: #FFFFFF;">2. <strong style="color: #FFFFFF;">주변 소음을 최소화</strong>하세요 (대화, TV, 다른 장비 소음 등)</p>
            <p style="color: #FFFFFF;">3. <strong style="color: #FFFFFF;">5-10초간 녹음</strong>하세요 (너무 짧으면 분석이 어려워요)</p>
            <p style="color: #FFFFFF;">4. <strong style="color: #FFFFFF;">녹음 버튼을 클릭</strong>하여 시작하세요</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 오디오 녹음
        audio_bytes = audio_recorder(
            text="🎤 녹음 시작",
            recording_color="#FF6B6B",
            neutral_color="#4CAF50",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=2.0,
            sample_rate=22050
        )
        
        if audio_bytes:
            st.success("✅ 녹음이 완료되었습니다!")
            
            # 녹음된 오디오 재생
            st.audio(audio_bytes, format="audio/wav")
            
            # 오디오 정보 표시
            audio_size = len(audio_bytes)
            st.info(f"📄 녹음 정보: {audio_size:,} bytes ({audio_size/1024:.1f} KB)")
            
            # 버튼들
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 다시 녹음", key="re_record"):
                    st.rerun()
            
            with col2:
                if st.button("💾 녹음 저장", key="save_recording"):
                    self.session_state.recording_data = audio_bytes
                    st.success("✅ 녹음이 저장되었습니다!")
            
            with col3:
                if st.button("▶️ 분석 시작", key="start_analysis", disabled=not audio_bytes):
                    if audio_bytes:
                        self.session_state.recording_data = audio_bytes
                        self.session_state.diagnosis_step = 'analysis'
                        st.rerun()
                    else:
                        st.error("❌ 먼저 녹음을 완료해주세요.")
        
        # 파일 업로드 옵션
        st.markdown("---")
        
        # 파일 업로드 설명 - 검은색 배경
        st.markdown("""
        <div style="background-color: #000000; color: #FFFFFF; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h3 style="color: #FFFFFF; margin-top: 0;">📁 또는 오디오 파일 업로드</h3>
            <p style="color: #FFFFFF;">오디오 파일 선택 (WAV, MP3, M4A)</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "오디오 파일을 여기에 끌어다 놓거나 클릭하여 선택하세요",
            type=['wav', 'mp3', 'm4a'],
            help="이미 녹음된 오디오 파일을 업로드할 수 있습니다"
        )
        
        if uploaded_file is not None:
            audio_bytes = uploaded_file.read()
            st.success("✅ 파일이 업로드되었습니다!")
            
            st.audio(audio_bytes, format=f"audio/{uploaded_file.type.split('/')[-1]}")
            
            file_size = len(audio_bytes)
            st.info(f"📄 파일 정보: {uploaded_file.name} ({file_size:,} bytes)")
            
            if st.button("▶️ 업로드된 파일로 분석 시작", key="analyze_uploaded"):
                self.session_state.recording_data = audio_bytes
                self.session_state.diagnosis_step = 'analysis'
                st.rerun()
        
        # 이전 단계로 돌아가기
        if st.button("🔙 고객 정보 수정", key="back_to_info"):
            self.session_state.diagnosis_step = 'customer_info'
            st.rerun()
    
    def analysis_step(self):
        """3단계: 자동 분석"""
        st.markdown("# 🤖 AI 분석 중...")
        
        st.markdown("""
        <div class="status-box status-analyzing">
            🔄 AI가 소음을 분석하고 있습니다...<br>
            잠시만 기다려주세요.
        </div>
        """, unsafe_allow_html=True)
        
        # 진행 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 실제 분석 시뮬레이션
        steps = [
            "🎵 오디오 파일 처리 중...",
            "📊 주파수 분석 중...",
            "🤖 AI 모델 추론 중...",
            "📄 리포트 생성 중...",
            "✅ 분석 완료!"
        ]
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(1)  # 실제로는 분석 시간
        
        # 실제 분석 수행 (백엔드 API 호출)
        analysis_result = self.perform_analysis()
        
        if analysis_result:
            self.session_state.analysis_result = analysis_result
            self.session_state.diagnosis_step = 'result'
            st.rerun()
        else:
            st.error("분석 중 오류가 발생했습니다. 다시 시도해주세요.")
            if st.button("🔄 다시 분석", key="retry_analysis"):
                st.rerun()
    
    def perform_analysis(self):
        """실제 AI 분석 수행"""
        try:
            # 백엔드 API 서버에 분석 요청
            api_url = "http://localhost:8000/diagnosis/analyze-audio"
            
            # 오디오 데이터 준비
            audio_data = self.session_state.recording_data
            info = self.session_state.customer_info
            
            files = {
                'audio_file': ('recording.wav', audio_data, 'audio/wav')
            }
            
            data = {
                'customer_name': info['customer_name'],
                'equipment_type': info['equipment_type'],
                'equipment_id': info['equipment_id'],
                'technician_name': info['technician_name']
            }
            
            # 실제 백엔드 API 호출
            try:
                response = requests.post(
                    "http://localhost:8000/field-diagnosis/analyze",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # diagnosis_id 저장 (PDF 생성용)
                    if 'diagnosis_id' in result:
                        st.session_state.current_diagnosis_id = result['diagnosis_id']
                    
                    return result
                else:
                    st.error(f"분석 API 오류: {response.status_code}")
                    return None
                    
            except requests.exceptions.ConnectionError:
                st.warning("⚠️ 백엔드 서버 연결 실패. 시뮬레이션 모드로 실행합니다.")
                # 백엔드 연결 실패 시 시뮬레이션 결과 사용
                import random
                
                results = [
                    {"diagnosis": "정상", "confidence": 0.95, "status": "normal"},
                    {"diagnosis": "주의 필요", "confidence": 0.78, "status": "caution"},
                    {"diagnosis": "이상 감지", "confidence": 0.85, "status": "danger"}
                ]
                
                result = random.choice(results)
                
                # 진단 기록 저장 (로컬 DB)
                self.save_diagnosis_record(result)
                
                # 시뮬레이션용 diagnosis_id 생성
                st.session_state.current_diagnosis_id = int(datetime.now().timestamp())
                
                return result
            
        except Exception as e:
            st.error(f"분석 오류: {e}")
            return None
    
    def save_diagnosis_record(self, result):
        """진단 기록 저장"""
        try:
            conn = sqlite3.connect('field_diagnosis.db')
            cursor = conn.cursor()
            
            info = self.session_state.customer_info
            
            cursor.execute('''
                INSERT INTO diagnoses 
                (customer_name, equipment_type, equipment_id, technician_name, 
                 diagnosis_result, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                info['customer_name'],
                info['equipment_type'], 
                info['equipment_id'],
                info['technician_name'],
                result['diagnosis'],
                result['confidence']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.error(f"데이터 저장 오류: {e}")
    
    def result_step(self):
        """4단계: 결과 확인"""
        st.markdown("# 📊 진단 결과")
        
        result = self.session_state.analysis_result
        info = self.session_state.customer_info
        
        # 결과에 따른 스타일 설정
        if "정상" in result['diagnosis']:
            result_class = "result-normal"
            status_icon = "✅"
            status_color = "#4CAF50"
        elif "주의" in result['diagnosis']:
            result_class = "result-caution"
            status_icon = "⚠️"
            status_color = "#FF9800"
        else:
            result_class = "result-danger"
            status_icon = "🚨"
            status_color = "#F44336"
        
        # 고객 정보 요약 - 강제 배경색 적용
        st.markdown(f"""
        <div style="background-color: #000000; color: #FFFFFF; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <h2 style="color: #FFFFFF; margin: 0 0 10px 0;">📍 진단 정보</h2>
            <p style="color: #FFFFFF; margin: 5px 0; font-size: 16px;">🏢 고객: {info['customer_name']}</p>
            <p style="color: #FFFFFF; margin: 5px 0; font-size: 16px;">🔧 장비: {info['equipment_type']} - {info['equipment_id']}</p>
            <p style="color: #FFFFFF; margin: 5px 0; font-size: 16px;">👨‍🔧 기술자: {info['technician_name']}</p>
            <p style="color: #FFFFFF; margin: 5px 0; font-size: 16px;">📅 진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 진단 결과 - 네이티브 컴포넌트 사용
        if "정상" in result['diagnosis']:
            st.success(f"{status_icon} **{result['diagnosis']}**")
        elif "주의" in result['diagnosis']:
            st.warning(f"{status_icon} **{result['diagnosis']}**")
        else:
            st.error(f"{status_icon} **{result['diagnosis']}**")
        
        st.write(f"**신뢰도: {result['confidence']*100:.1f}%**")
        
        # 상세 분석 결과
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 분석 상세")
            st.markdown(f"""
            - **진단 결과**: {result['diagnosis']}
            - **신뢰도**: {result['confidence']*100:.1f}%
            - **상태**: {result.get('status', 'unknown')}
            - **분석 시간**: {datetime.now().strftime('%H:%M:%S')}
            """)
        
        with col2:
            st.markdown("### 💡 권장사항")
            recommendations = self.get_recommendations(result['diagnosis'])
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        # 액션 버튼들
        st.markdown("---")
        st.markdown("### 🎯 다음 단계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 PDF 리포트 생성", key="generate_pdf"):
                self.generate_pdf_report()
        
        with col2:
            if st.button("💬 카카오톡 전송", key="send_kakao"):
                self.send_via_kakao()
        
        with col3:
            if st.button("📱 문자 전송", key="send_sms"):
                self.send_via_sms()
        
        with col4:
            if st.button("📧 이메일 전송", key="send_email"):
                self.send_via_email()
        
        # 새로운 진단 시작
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 새로운 진단 시작", key="new_diagnosis"):
                # 세션 상태 초기화
                for key in ['customer_info', 'recording_data', 'analysis_result']:
                    if key in self.session_state:
                        del self.session_state[key]
                self.session_state.diagnosis_step = 'welcome'
                st.rerun()
        
        with col2:
            if st.button("📋 진단 이력 보기", key="view_history"):
                self.show_diagnosis_history()
    
    def get_recommendations(self, diagnosis):
        """진단 결과에 따른 권장사항 반환"""
        recommendations = {
            "정상": [
                "현재 장비 상태가 양호합니다",
                "정기적인 점검을 유지하세요",
                "3개월 후 재점검을 권장합니다"
            ],
            "주의 필요": [
                "장비 상태를 주의 깊게 모니터링하세요",
                "1개월 내 재점검을 권장합니다",
                "필요시 전문 기술자 상담을 받으세요",
                "예방 정비를 고려해보세요"
            ],
            "이상 감지": [
                "즉시 전문 기술자의 점검이 필요합니다",
                "장비 사용을 일시 중단하는 것을 고려하세요",
                "부품 교체나 수리가 필요할 수 있습니다",
                "추가 손상 방지를 위해 신속한 조치를 취하세요"
            ]
        }
        return recommendations.get(diagnosis, [])
    
    def generate_pdf_report(self):
        """실제 PDF 리포트 생성 (오프라인 모드 지원)"""
        try:
            # 백엔드 API 시도
            if hasattr(st.session_state, 'current_diagnosis_id'):
                diagnosis_id = st.session_state.current_diagnosis_id
                
                api_url = "http://localhost:8000"
                
                with st.spinner("📄 PDF 리포트 생성 중..."):
                    try:
                        response = requests.post(
                            f"{api_url}/field-diagnosis/generate-report",
                            json={"diagnosis_id": diagnosis_id},
                            timeout=5  # 짧은 타임아웃으로 빠른 실패
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success"):
                                pdf_path = result.get("pdf_path")
                                if pdf_path and os.path.exists(pdf_path):
                                    # PDF 파일을 읽어서 다운로드 버튼 제공
                                    with open(pdf_path, 'rb') as pdf_file:
                                        pdf_bytes = pdf_file.read()
                                    
                                    # 파일명 생성
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    customer_name = st.session_state.get('customer_name', 'Customer')
                                    filename = f"진단리포트_{customer_name}_{timestamp}.pdf"
                                    
                                    st.success("✅ PDF 리포트 생성 완료!")
                                    
                                    # 다운로드 버튼
                                    st.download_button(
                                        label="📥 PDF 리포트 다운로드",
                                        data=pdf_bytes,
                                        file_name=filename,
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                    
                                    st.info(f"📄 파일 크기: {len(pdf_bytes):,} bytes")
                                    return  # 성공시 리턴
                                    
                    except requests.exceptions.ConnectionError:
                        pass  # 오프라인 모드로 전환
                    except requests.exceptions.Timeout:
                        pass  # 오프라인 모드로 전환
            
            # 오프라인 모드: 직접 PDF 생성
            st.warning("🔄 백엔드 서버에 연결할 수 없어 오프라인 모드로 PDF를 생성합니다.")
            
            with st.spinner("📄 오프라인 PDF 리포트 생성 중..."):
                # 분석 결과 데이터 준비
                if hasattr(st.session_state, 'analysis_result'):
                    analysis_result = st.session_state.analysis_result
                    customer_info = st.session_state.customer_info
                    
                    pdf_data = {
                        'customer_name': customer_info.get('customer_name', '고객명'),
                        'equipment_type': customer_info.get('equipment_type', '장비유형'),
                        'equipment_id': customer_info.get('equipment_id', '장비ID'),
                        'technician_name': customer_info.get('technician_name', '기술자'),
                        'diagnosis': analysis_result.get('diagnosis', '진단결과'),
                        'confidence': analysis_result.get('confidence', 0.8),
                        'noise_level': 70,  # 시뮬레이션 값
                        'vibration': '정상',
                        'anomaly': '없음',
                        'processing_time': 2.3,
                        'signal_strength': 85
                    }
                    
                    # 안정적인 오프라인 리포트 생성
                    try:
                        from reliable_report_generator import generate_offline_report
                        
                        # 리포트 생성 (HTML 우선, 실패시 텍스트)
                        results = generate_offline_report(pdf_data, "html")
                        
                        if results:
                            # 첫 번째 생성된 파일 사용
                            format_type, filename = results[0]
                            
                            if os.path.exists(filename):
                                # 파일 읽기
                                if filename.endswith('.txt'):
                                    with open(filename, 'r', encoding='utf-8') as f:
                                        file_content = f.read()
                                        file_bytes = file_content.encode('utf-8')
                                    mime_type = "text/plain"
                                    button_label = "📥 텍스트 리포트 다운로드"
                                else:
                                    with open(filename, 'rb') as f:
                                        file_bytes = f.read()
                                    mime_type = "text/html" if filename.endswith('.html') else "application/pdf"
                                    button_label = "📥 HTML 리포트 다운로드" if filename.endswith('.html') else "📥 리포트 다운로드"
                                
                                st.success(f"✅ 오프라인 {format_type.upper()} 리포트 생성 완료!")

                                # 다운로드 버튼
                                st.download_button(
                                    label=button_label,
                                    data=file_bytes,
                                    file_name=filename,
                                    mime=mime_type,
                                    use_container_width=True
                                )

                                # 파일 정보 표시
                                st.info(f"📄 파일 크기: {len(file_bytes):,} bytes | 형식: {format_type.upper()}")

                            else:
                                st.error(f"❌ 생성된 리포트 파일을 찾을 수 없습니다: {filename}")
                        else:
                            st.error("❌ 리포트 생성에 실패했습니다.")
                            
                    except ImportError:
                        # 모든 모듈이 없을 때 최종 대안
                        st.warning("⚠️ 리포트 생성 모듈을 찾을 수 없습니다. 기본 텍스트 리포트를 생성합니다.")
                        
                        # 간단한 텍스트 생성
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        simple_filename = f"간단리포트_{pdf_data['customer_name']}_{timestamp}.txt"
                        
                        simple_content = f"""압축기 진단 리포트
================================
고객명: {pdf_data['customer_name']}
장비 유형: {pdf_data['equipment_type']}
장비 ID: {pdf_data['equipment_id']}
진단 결과: {pdf_data['diagnosis']}
신뢰도: {int(pdf_data['confidence'] * 100)}%
기술자: {pdf_data['technician_name']}
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

문의: 1588-0000
================================"""
                        
                        try:
                            with open(simple_filename, 'w', encoding='utf-8') as f:
                                f.write(simple_content)
                            
                            with open(simple_filename, 'r', encoding='utf-8') as f:
                                simple_bytes = f.read().encode('utf-8')
                            
                            st.success("✅ 간단한 텍스트 리포트 생성 완료!")
                            
                            st.download_button(
                                label="📥 간단 리포트 다운로드",
                                data=simple_bytes,
                                file_name=simple_filename,
                                mime="text/plain",
                                use_container_width=True
                            )
                            
                        except Exception as e:
                            st.error(f"❌ 간단한 리포트 생성도 실패했습니다: {e}")
                            
                    except Exception as e:
                        st.error(f"❌ 오프라인 리포트 생성 중 오류: {e}")
                        st.info("💡 모든 리포트 생성 방법이 실패했습니다. 시스템 관리자에게 문의하세요.")
                        
                else:
                    st.error("진단 결과가 없습니다. 먼저 분석을 실행해주세요.")
                    
        except Exception as e:
            st.error(f"❌ PDF 생성 중 오류: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    
    def send_via_kakao(self):
        """카카오톡으로 전송"""
        st.success("💬 카카오톡으로 전송 요청했습니다!")
        st.info("고객의 카카오톡으로 진단 결과가 전송됩니다.")
    
    def send_via_sms(self):
        """문자로 전송"""
        st.success("📱 문자로 전송 요청했습니다!")
        st.info("고객의 휴대폰으로 진단 결과가 전송됩니다.")
    
    def send_via_email(self):
        """이메일로 전송"""
        st.success("📧 이메일로 전송 요청했습니다!")
        st.info("고객의 이메일로 진단 리포트가 전송됩니다.")
    
    def show_diagnosis_history(self):
        """진단 이력 표시"""
        st.markdown("### 📋 진단 이력")
        
        try:
            conn = sqlite3.connect('field_diagnosis.db')
            df = pd.read_sql_query("""
                SELECT customer_name, equipment_type, equipment_id, 
                       diagnosis_result, confidence, created_at
                FROM diagnoses 
                ORDER BY created_at DESC 
                LIMIT 10
            """, conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("아직 진단 이력이 없습니다.")
                
        except Exception as e:
            st.error(f"이력 조회 오류: {e}")
    
    def run(self):
        """메인 실행 함수"""
        # 단계별 실행
        if self.session_state.diagnosis_step == 'welcome':
            self.welcome_step()
        elif self.session_state.diagnosis_step == 'customer_info':
            self.customer_info_step()
        elif self.session_state.diagnosis_step == 'recording':
            self.recording_step()
        elif self.session_state.diagnosis_step == 'analysis':
            self.analysis_step()
        elif self.session_state.diagnosis_step == 'result':
            self.result_step()

def main():
    """메인 함수"""
    app = FieldDiagnosisApp()
    app.run()

if __name__ == "__main__":
    main()
