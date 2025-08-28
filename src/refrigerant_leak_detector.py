# refrigerant_leak_detector.py - 냉매 부족 전용 진단 시스템
import streamlit as st
import numpy as np
import pandas as pd
import librosa
import sqlite3
from datetime import datetime
import os
import plotly.graph_objects as go
import plotly.express as px
from audio_recorder_streamlit import audio_recorder
import io
import time

# 페이지 설정
st.set_page_config(
    page_title="🧊 냉매 부족 진단 시스템",
    page_icon="🧊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

class RefrigerantLeakDetector:
    """냉매 부족으로 인한 압축기 과부하 전용 진단 시스템"""
    
    def __init__(self):
        self.init_database()
        self.init_session_state()
        
        # 냉매 부족 특화 임계값
        self.frequency_thresholds = {
            'low_freq_energy': 0.15,      # 저주파 에너지 비율 (압축기 부하)
            'mid_freq_peak': 800,         # 중주파 피크 (냉매 흐름)
            'high_freq_noise': 0.08,      # 고주파 노이즈 (시스템 스트레스)
            'harmonic_distortion': 0.25,  # 고조파 왜곡
            'rms_threshold': 0.02         # RMS 임계값
        }
        
        # 냉매 부족 진단 키워드
        self.refrigerant_symptoms = {
            'low_cooling': '냉각 성능 저하',
            'high_pressure': '고압 상승',
            'compressor_overload': '압축기 과부하',
            'frequent_cycling': '빈번한 on/off',
            'ice_formation': '증발기 결빙',
            'hot_compressor': '압축기 과열'
        }
    
    def init_database(self):
        """냉매 진단 전용 데이터베이스 초기화"""
        conn = sqlite3.connect('refrigerant_diagnosis.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refrigerant_diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                equipment_id TEXT NOT NULL,
                location TEXT NOT NULL,
                technician_name TEXT NOT NULL,
                
                -- 현장 관찰
                cooling_performance TEXT,  -- excellent/good/poor/very_poor
                compressor_temperature TEXT,  -- normal/warm/hot/very_hot
                frost_formation TEXT,  -- none/light/moderate/heavy
                cycling_frequency TEXT,  -- normal/frequent/continuous
                
                -- 오디오 분석 결과
                audio_path TEXT,
                low_freq_energy REAL,
                mid_freq_peak REAL,
                high_freq_noise REAL,
                harmonic_distortion REAL,
                rms_level REAL,
                
                -- 진단 결과
                refrigerant_level TEXT,  -- sufficient/low/very_low/empty
                leak_probability REAL,
                urgency_level TEXT,  -- normal/attention/urgent/critical
                recommended_action TEXT,
                
                -- 메타데이터
                diagnosis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score REAL,
                follow_up_needed BOOLEAN DEFAULT 0
            )
        ''')
        
        # 냉매 부족 패턴 학습 데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refrigerant_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT NOT NULL,
                low_freq_min REAL,
                low_freq_max REAL,
                mid_freq_min REAL, 
                mid_freq_max REAL,
                high_freq_min REAL,
                high_freq_max REAL,
                rms_min REAL,
                rms_max REAL,
                description TEXT,
                severity TEXT  -- normal/warning/critical
            )
        ''')
        
        # 기본 패턴 데이터 삽입
        patterns = [
            ('정상_냉매량', 0.05, 0.12, 600, 1000, 0.02, 0.06, 0.008, 0.015, '정상적인 냉매량, 안정적 운전', 'normal'),
            ('경미한_냉매부족', 0.12, 0.18, 500, 800, 0.06, 0.10, 0.015, 0.025, '약간의 냉매 부족, 모니터링 필요', 'warning'),
            ('중간_냉매부족', 0.18, 0.28, 400, 600, 0.10, 0.15, 0.025, 0.040, '상당한 냉매 부족, 즉시 점검', 'warning'),
            ('심각한_냉매부족', 0.28, 0.45, 200, 400, 0.15, 0.25, 0.040, 0.070, '심각한 냉매 부족, 긴급 수리', 'critical'),
            ('냉매_거의없음', 0.45, 1.0, 100, 300, 0.25, 0.50, 0.070, 0.150, '냉매 거의 없음, 즉시 중단', 'critical')
        ]
        
        for pattern in patterns:
            cursor.execute('''
                INSERT OR IGNORE INTO refrigerant_patterns 
                (pattern_name, low_freq_min, low_freq_max, mid_freq_min, mid_freq_max,
                 high_freq_min, high_freq_max, rms_min, rms_max, description, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', pattern)
        
        conn.commit()
        conn.close()
    
    def init_session_state(self):
        """세션 상태 초기화"""
        if 'current_diagnosis' not in st.session_state:
            st.session_state.current_diagnosis = None
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = None
    
    def analyze_refrigerant_audio(self, audio_data):
        """냉매 부족 특화 오디오 분석"""
        try:
            # 오디오 데이터를 임시 파일로 저장
            temp_path = "temp_audio.wav"
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # librosa로 오디오 로드
            audio, sr = librosa.load(temp_path, sr=22050)
            
            # 1. 주파수 분석 (FFT)
            fft = np.fft.fft(audio)
            frequencies = np.fft.fftfreq(len(audio), 1/sr)
            power_spectrum = np.abs(fft) ** 2
            
            # 양의 주파수만 사용
            positive_mask = frequencies > 0
            frequencies = frequencies[positive_mask]
            power_spectrum = power_spectrum[positive_mask]
            
            # 2. 주파수 대역별 에너지 분석
            total_energy = np.sum(power_spectrum)
            
            # 저주파 에너지 (0-200Hz) - 압축기 기계적 소음
            low_freq_mask = (frequencies >= 20) & (frequencies <= 200)
            low_freq_energy = np.sum(power_spectrum[low_freq_mask]) / total_energy
            
            # 중주파 피크 (200-1500Hz) - 냉매 흐름 소음
            mid_freq_mask = (frequencies >= 200) & (frequencies <= 1500)
            if np.any(mid_freq_mask):
                mid_freq_peak = frequencies[mid_freq_mask][np.argmax(power_spectrum[mid_freq_mask])]
            else:
                mid_freq_peak = 0
            
            # 고주파 노이즈 (1500-8000Hz) - 시스템 스트레스
            high_freq_mask = (frequencies >= 1500) & (frequencies <= 8000)
            high_freq_energy = np.sum(power_spectrum[high_freq_mask]) / total_energy
            
            # 3. 시간 영역 분석
            rms_level = np.sqrt(np.mean(audio ** 2))
            peak_level = np.max(np.abs(audio))
            crest_factor = peak_level / rms_level if rms_level > 0 else 0
            
            # 4. 고조파 왜곡 분석 (압축기 부하 상태)
            # 기본 주파수와 고조파의 비율
            fundamental_freq = 50  # 기본 주파수 (Hz)
            harmonic_energy = 0
            
            for harmonic in range(2, 8):  # 2차~7차 고조파
                harmonic_freq = fundamental_freq * harmonic
                harmonic_mask = (frequencies >= harmonic_freq - 5) & (frequencies <= harmonic_freq + 5)
                if np.any(harmonic_mask):
                    harmonic_energy += np.sum(power_spectrum[harmonic_mask])
            
            harmonic_distortion = harmonic_energy / total_energy
            
            # 5. 스펙트럼 특성 분석
            spectral_centroid = np.sum(frequencies * power_spectrum) / np.sum(power_spectrum)
            spectral_rolloff = self.calculate_spectral_rolloff(frequencies, power_spectrum, 0.85)
            
            # 임시 파일 삭제
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return {
                'low_freq_energy': low_freq_energy,
                'mid_freq_peak': mid_freq_peak,
                'high_freq_noise': high_freq_energy,
                'harmonic_distortion': harmonic_distortion,
                'rms_level': rms_level,
                'crest_factor': crest_factor,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'frequencies': frequencies[:1000],  # 시각화용
                'power_spectrum': power_spectrum[:1000]
            }
            
        except Exception as e:
            st.error(f"오디오 분석 실패: {e}")
            return None
    
    def calculate_spectral_rolloff(self, frequencies, power_spectrum, rolloff_ratio=0.85):
        """스펙트럼 롤오프 계산"""
        cumulative_energy = np.cumsum(power_spectrum)
        total_energy = cumulative_energy[-1]
        rolloff_threshold = rolloff_ratio * total_energy
        
        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold)[0]
        if len(rolloff_idx) > 0:
            return frequencies[rolloff_idx[0]]
        else:
            return frequencies[-1]
    
    def diagnose_refrigerant_level(self, audio_features, field_observations):
        """냉매 수준 진단"""
        if audio_features is None:
            return None
        
        # 진단 점수 계산
        score = 0
        confidence = 0
        details = []
        
        # 1. 저주파 에너지 분석 (압축기 부하)
        low_freq = audio_features['low_freq_energy']
        if low_freq > 0.28:
            score += 40
            details.append(f"🔴 높은 저주파 에너지 ({low_freq:.3f}) - 압축기 과부하 의심")
        elif low_freq > 0.18:
            score += 25
            details.append(f"🟡 상승된 저주파 에너지 ({low_freq:.3f}) - 부하 증가")
        elif low_freq > 0.12:
            score += 10
            details.append(f"🟢 약간 높은 저주파 에너지 ({low_freq:.3f}) - 정상 범위")
        else:
            details.append(f"✅ 정상 저주파 에너지 ({low_freq:.3f})")
        
        # 2. 중주파 피크 분석 (냉매 흐름)
        mid_freq = audio_features['mid_freq_peak']
        if mid_freq < 300:
            score += 30
            details.append(f"🔴 낮은 냉매 흐름 주파수 ({mid_freq:.0f}Hz) - 냉매 부족")
        elif mid_freq < 500:
            score += 20
            details.append(f"🟡 감소된 냉매 흐름 ({mid_freq:.0f}Hz)")
        elif mid_freq < 700:
            score += 5
            details.append(f"🟢 약간 낮은 냉매 흐름 ({mid_freq:.0f}Hz)")
        else:
            details.append(f"✅ 정상 냉매 흐름 ({mid_freq:.0f}Hz)")
        
        # 3. 고주파 노이즈 (시스템 스트레스)
        high_freq = audio_features['high_freq_noise']
        if high_freq > 0.20:
            score += 20
            details.append(f"🔴 높은 시스템 노이즈 ({high_freq:.3f}) - 스트레스 상태")
        elif high_freq > 0.12:
            score += 10
            details.append(f"🟡 상승된 노이즈 레벨 ({high_freq:.3f})")
        else:
            details.append(f"✅ 정상 노이즈 레벨 ({high_freq:.3f})")
        
        # 4. RMS 레벨 (전체적인 진동)
        rms = audio_features['rms_level']
        if rms > 0.050:
            score += 15
            details.append(f"🔴 높은 진동 레벨 ({rms:.3f}) - 시스템 부하")
        elif rms > 0.030:
            score += 8
            details.append(f"🟡 상승된 진동 ({rms:.3f})")
        else:
            details.append(f"✅ 정상 진동 레벨 ({rms:.3f})")
        
        # 5. 현장 관찰 점수 추가
        field_score = 0
        if field_observations.get('cooling_performance') in ['poor', 'very_poor']:
            field_score += 20
            details.append("🔴 현장 확인: 냉각 성능 저하")
        
        if field_observations.get('compressor_temperature') in ['hot', 'very_hot']:
            field_score += 15
            details.append("🔴 현장 확인: 압축기 과열")
        
        if field_observations.get('frost_formation') in ['heavy', 'moderate']:
            field_score += 10
            details.append("🟡 현장 확인: 과도한 결빙")
        
        if field_observations.get('cycling_frequency') == 'frequent':
            field_score += 10
            details.append("🟡 현장 확인: 빈번한 운전")
        
        # 총 점수 계산
        total_score = min(score + field_score, 100)
        
        # 진단 결과 결정
        if total_score >= 70:
            level = "매우 부족"
            urgency = "긴급"
            action = "즉시 운전 중단 후 냉매 보충 및 누출 점검"
            confidence = 0.9
        elif total_score >= 50:
            level = "부족"
            urgency = "주의"
            action = "냉매량 점검 및 누출 확인, 가능한 빨리 보충"
            confidence = 0.8
        elif total_score >= 30:
            level = "약간 부족"
            urgency = "모니터링"
            action = "정기적인 냉매량 점검, 성능 모니터링 강화"
            confidence = 0.7
        else:
            level = "정상"
            urgency = "정상"
            action = "현재 상태 유지, 정기 점검 지속"
            confidence = 0.6
        
        return {
            'refrigerant_level': level,
            'urgency_level': urgency,
            'recommended_action': action,
            'confidence_score': confidence,
            'total_score': total_score,
            'analysis_details': details,
            'audio_features': audio_features
        }
    
    def show_main_interface(self):
        """메인 인터페이스"""
        st.title("🧊 냉매 부족 전용 진단 시스템")
        st.markdown("### 압축기 과부하 → 냉매 부족 집중 진단")
        
        # 진단 단계 표시
        if st.session_state.current_diagnosis is None:
            self.show_diagnosis_setup()
        else:
            diagnosis = st.session_state.current_diagnosis
            
            if diagnosis['step'] == 'observation':
                self.show_field_observation()
            elif diagnosis['step'] == 'recording':
                self.show_audio_recording()
            elif diagnosis['step'] == 'analysis':
                self.show_analysis_results()
    
    def show_diagnosis_setup(self):
        """진단 설정"""
        st.subheader("📋 새로운 냉매 진단 시작")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("고객명")
            equipment_id = st.text_input("장비 ID")
            location = st.text_input("설치 위치")
        
        with col2:
            technician_name = st.text_input("기술자명")
            equipment_type = st.selectbox("장비 유형", 
                ["냉동고", "냉장고", "에어컨", "히트펌프", "산업용 냉동기"])
            
        if st.button("🚀 진단 시작", type="primary"):
            if all([customer_name, equipment_id, location, technician_name]):
                st.session_state.current_diagnosis = {
                    'customer_name': customer_name,
                    'equipment_id': equipment_id,
                    'location': location,
                    'technician_name': technician_name,
                    'equipment_type': equipment_type,
                    'step': 'observation',
                    'start_time': datetime.now()
                }
                st.rerun()
            else:
                st.error("모든 필수 정보를 입력해주세요.")
    
    def show_field_observation(self):
        """현장 관찰 단계"""
        diagnosis = st.session_state.current_diagnosis
        
        st.subheader("👁️ 현장 상태 확인")
        
        # 진단 정보 표시
        with st.expander("📋 진단 정보", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**고객**: {diagnosis['customer_name']}")
                st.write(f"**장비**: {diagnosis['equipment_type']} - {diagnosis['equipment_id']}")
            with col2:
                st.write(f"**위치**: {diagnosis['location']}")
                st.write(f"**기술자**: {diagnosis['technician_name']}")
        
        st.markdown("---")
        
        # 현장 관찰 체크리스트
        st.markdown("### 🔍 냉매 부족 증상 체크")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 냉각 성능")
            cooling_performance = st.radio(
                "냉각 상태는?",
                ["excellent", "good", "poor", "very_poor"],
                format_func=lambda x: {
                    "excellent": "🟢 매우 좋음",
                    "good": "🟡 양호", 
                    "poor": "🟠 불량",
                    "very_poor": "🔴 매우 불량"
                }[x],
                key="cooling"
            )
            
            st.markdown("#### 압축기 온도")
            compressor_temp = st.radio(
                "압축기 표면 온도는?",
                ["normal", "warm", "hot", "very_hot"],
                format_func=lambda x: {
                    "normal": "🟢 정상 (미지근)",
                    "warm": "🟡 따뜻함",
                    "hot": "🟠 뜨거움", 
                    "very_hot": "🔴 매우 뜨거움"
                }[x],
                key="temp"
            )
        
        with col2:
            st.markdown("#### 결빙 상태")
            frost_formation = st.radio(
                "증발기 결빙 정도는?",
                ["none", "light", "moderate", "heavy"],
                format_func=lambda x: {
                    "none": "🟢 없음",
                    "light": "🟡 약간",
                    "moderate": "🟠 보통",
                    "heavy": "🔴 심함"
                }[x],
                key="frost"
            )
            
            st.markdown("#### 운전 패턴")
            cycling_frequency = st.radio(
                "압축기 운전 패턴은?",
                ["normal", "frequent", "continuous"],
                format_func=lambda x: {
                    "normal": "🟢 정상 (적절한 간격)",
                    "frequent": "🟡 빈번함 (자주 켜짐)",
                    "continuous": "🔴 연속 운전"
                }[x],
                key="cycling"
            )
        
        # 추가 관찰사항
        additional_symptoms = st.multiselect(
            "🚨 추가로 발견된 증상 (해당하는 것 모두 선택)",
            [
                "압축기에서 이상 소음",
                "배관에서 가스 냄새", 
                "오일 얼룩 발견",
                "배관 연결부 부식",
                "과도한 전력 소모",
                "온도 편차 큼",
                "습도 조절 불량"
            ]
        )
        
        notes = st.text_area("기타 특이사항")
        
        if st.button("🎤 오디오 녹음 단계로", type="primary"):
            diagnosis['field_observations'] = {
                'cooling_performance': cooling_performance,
                'compressor_temperature': compressor_temp,
                'frost_formation': frost_formation,
                'cycling_frequency': cycling_frequency,
                'additional_symptoms': additional_symptoms,
                'notes': notes
            }
            diagnosis['step'] = 'recording'
            st.session_state.current_diagnosis = diagnosis
            st.rerun()
    
    def show_audio_recording(self):
        """오디오 녹음 단계"""
        diagnosis = st.session_state.current_diagnosis
        
        st.subheader("🎤 압축기 소음 녹음")
        
        # 냉매 부족 특화 녹음 가이드
        st.info("""
        🎯 **냉매 부족 진단을 위한 특별 녹음 가이드**
        
        🔊 **압축기 근처 녹음 (1-2미터)**
        - 압축기가 **운전 중**일 때 녹음
        - **15-20초** 충분히 녹음 (냉매 흐름 패턴 캐치)
        - 배관 연결부 근처도 포함
        
        🎵 **냉매 흐름 소음 포착**
        - 압축기 → 응축기 → 증발기 순서로 이동하며 녹음
        - 특히 **팽창밸브 근처** 소음 중요
        - **"쉿~" 소리나 "거품" 소리** 주의 깊게 청취
        """)
        
        # 오디오 녹음
        audio_bytes = audio_recorder(
            text="🎤 냉매 진단용 녹음 시작",
            recording_color="#e74c3c",
            neutral_color="#3498db", 
            icon_name="snowflake",
            icon_size="2x",
        )
        
        st.write("**또는**")
        uploaded_file = st.file_uploader("🎵 오디오 파일 업로드", 
                                       type=['wav', 'mp3', 'm4a'])
        
        if audio_bytes or uploaded_file:
            audio_data = audio_bytes if audio_bytes else uploaded_file.read()
            
            # 오디오 재생
            st.audio(audio_data, format='audio/wav')
            
            # 녹음 품질 확인
            col1, col2, col3 = st.columns(3)
            
            with col1:
                recording_quality = st.selectbox("녹음 품질", [1, 2, 3, 4, 5], index=3)
            with col2:
                compressor_running = st.selectbox("압축기 상태", ["운전중", "정지중", "불명"])
            with col3:
                background_noise = st.selectbox("주변 소음", ["낮음", "보통", "높음"])
            
            if st.button("🔍 냉매 진단 분석 시작", type="primary"):
                with st.spinner("🧊 냉매 부족 패턴을 분석 중입니다..."):
                    # 오디오 분석
                    audio_features = self.analyze_refrigerant_audio(audio_data)
                    
                    if audio_features:
                        # 진단 수행
                        diagnosis_result = self.diagnose_refrigerant_level(
                            audio_features, 
                            diagnosis['field_observations']
                        )
                        
                        if diagnosis_result:
                            # 오디오 저장
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            audio_filename = f"refrigerant_{diagnosis['customer_name']}_{timestamp}.wav"
                            audio_path = f"refrigerant_recordings/{audio_filename}"
                            
                            os.makedirs("refrigerant_recordings", exist_ok=True)
                            with open(audio_path, 'wb') as f:
                                f.write(audio_data)
                            
                            diagnosis['audio_path'] = audio_path
                            diagnosis['audio_features'] = audio_features
                            diagnosis['diagnosis_result'] = diagnosis_result
                            diagnosis['recording_metadata'] = {
                                'quality': recording_quality,
                                'compressor_running': compressor_running,
                                'background_noise': background_noise
                            }
                            diagnosis['step'] = 'analysis'
                            
                            st.session_state.current_diagnosis = diagnosis
                            st.success("✅ 분석 완료!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("진단 분석에 실패했습니다.")
                    else:
                        st.error("오디오 분석에 실패했습니다.")
        
        # 뒤로 가기
        if st.button("← 현장 관찰로 돌아가기"):
            diagnosis['step'] = 'observation'
            st.session_state.current_diagnosis = diagnosis
            st.rerun()
    
    def show_analysis_results(self):
        """분석 결과 표시"""
        diagnosis = st.session_state.current_diagnosis
        result = diagnosis['diagnosis_result']
        audio_features = diagnosis['audio_features']
        
        st.subheader("🧊 냉매 부족 진단 결과")
        
        # 결과 요약
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 냉매 수준
            level = result['refrigerant_level']
            if level == "정상":
                st.success(f"❄️ 냉매 수준: **{level}**")
            elif level in ["약간 부족"]:
                st.warning(f"🟡 냉매 수준: **{level}**")
            else:
                st.error(f"🚨 냉매 수준: **{level}**")
        
        with col2:
            # 긴급도
            urgency = result['urgency_level']
            if urgency == "정상":
                st.success(f"✅ 긴급도: **{urgency}**")
            elif urgency in ["모니터링", "주의"]:
                st.warning(f"⚠️ 긴급도: **{urgency}**")
            else:
                st.error(f"🚨 긴급도: **{urgency}**")
        
        with col3:
            # 신뢰도
            confidence = result['confidence_score']
            st.info(f"🎯 신뢰도: **{confidence:.1%}**")
        
        # 진단 점수 게이지
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = result['total_score'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "냉매 부족 위험도 점수"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 50], 'color': "yellow"},
                    {'range': [50, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # 권장 조치
        st.subheader("🔧 권장 조치사항")
        action = result['recommended_action']
        
        if result['urgency_level'] in ['긴급', 'critical']:
            st.error(f"🚨 **즉시 조치 필요**: {action}")
        elif result['urgency_level'] in ['주의', 'warning']:
            st.warning(f"⚠️ **주의 필요**: {action}")
        else:
            st.success(f"✅ **정상 범위**: {action}")
        
        # 상세 분석 결과
        with st.expander("🔍 상세 분석 결과", expanded=True):
            st.write("### 오디오 분석 세부사항")
            
            for detail in result['analysis_details']:
                st.write(f"- {detail}")
            
            # 주파수 스펙트럼 시각화
            if 'frequencies' in audio_features and 'power_spectrum' in audio_features:
                fig = px.line(
                    x=audio_features['frequencies'], 
                    y=audio_features['power_spectrum'],
                    title="주파수 스펙트럼 분석",
                    labels={'x': '주파수 (Hz)', 'y': '파워 스펙트럼'}
                )
                
                # 냉매 부족 특화 주파수 영역 표시
                fig.add_vrect(x0=20, x1=200, fillcolor="red", opacity=0.2, 
                             annotation_text="압축기 부하 영역", annotation_position="top left")
                fig.add_vrect(x0=200, x1=1500, fillcolor="blue", opacity=0.2,
                             annotation_text="냉매 흐름 영역", annotation_position="top")
                fig.add_vrect(x0=1500, x1=8000, fillcolor="green", opacity=0.2,
                             annotation_text="시스템 노이즈", annotation_position="top right")
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 현장 관찰 vs 오디오 분석 비교
        with st.expander("📊 현장 관찰 vs 오디오 분석 비교"):
            observations = diagnosis['field_observations']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**현장 관찰 결과**")
                st.write(f"- 냉각 성능: {observations['cooling_performance']}")
                st.write(f"- 압축기 온도: {observations['compressor_temperature']}")
                st.write(f"- 결빙 상태: {observations['frost_formation']}")
                st.write(f"- 운전 패턴: {observations['cycling_frequency']}")
            
            with col2:
                st.write("**오디오 분석 결과**")
                st.write(f"- 압축기 부하: {audio_features['low_freq_energy']:.3f}")
                st.write(f"- 냉매 흐름: {audio_features['mid_freq_peak']:.0f}Hz")
                st.write(f"- 시스템 노이즈: {audio_features['high_freq_noise']:.3f}")
                st.write(f"- 진동 레벨: {audio_features['rms_level']:.3f}")
        
        # 진단 저장 및 리포트
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 진단 결과 저장", type="primary"):
                self.save_diagnosis_result(diagnosis)
                st.success("✅ 진단 결과가 저장되었습니다!")
        
        with col2:
            if st.button("📄 리포트 생성"):
                self.generate_refrigerant_report(diagnosis)
        
        with col3:
            if st.button("🔄 새 진단 시작"):
                st.session_state.current_diagnosis = None
                st.rerun()
    
    def save_diagnosis_result(self, diagnosis):
        """진단 결과 데이터베이스 저장"""
        conn = sqlite3.connect('refrigerant_diagnosis.db')
        cursor = conn.cursor()
        
        result = diagnosis['diagnosis_result']
        observations = diagnosis['field_observations']
        audio_features = diagnosis['audio_features']
        
        cursor.execute('''
            INSERT INTO refrigerant_diagnoses (
                customer_name, equipment_id, location, technician_name,
                cooling_performance, compressor_temperature, frost_formation, cycling_frequency,
                audio_path, low_freq_energy, mid_freq_peak, high_freq_noise,
                harmonic_distortion, rms_level, refrigerant_level, leak_probability,
                urgency_level, recommended_action, confidence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            diagnosis['customer_name'], diagnosis['equipment_id'], 
            diagnosis['location'], diagnosis['technician_name'],
            observations['cooling_performance'], observations['compressor_temperature'],
            observations['frost_formation'], observations['cycling_frequency'],
            diagnosis['audio_path'], audio_features['low_freq_energy'],
            audio_features['mid_freq_peak'], audio_features['high_freq_noise'],
            audio_features['harmonic_distortion'], audio_features['rms_level'],
            result['refrigerant_level'], result['total_score'] / 100,
            result['urgency_level'], result['recommended_action'], result['confidence_score']
        ))
        
        conn.commit()
        conn.close()
    
    def generate_refrigerant_report(self, diagnosis):
        """냉매 진단 리포트 생성"""
        result = diagnosis['diagnosis_result']
        observations = diagnosis['field_observations']
        
        # 간단한 HTML 리포트 생성
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>냉매 부족 진단 리포트</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .urgent {{ background-color: #ffebee; border-color: #f44336; }}
                .warning {{ background-color: #fff3e0; border-color: #ff9800; }}
                .normal {{ background-color: #e8f5e8; border-color: #4caf50; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧊 냉매 부족 진단 리포트</h1>
                <p>{datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
            </div>
            
            <div class="section">
                <h2>📋 기본 정보</h2>
                <p><strong>고객명:</strong> {diagnosis['customer_name']}</p>
                <p><strong>장비 ID:</strong> {diagnosis['equipment_id']}</p>
                <p><strong>위치:</strong> {diagnosis['location']}</p>
                <p><strong>기술자:</strong> {diagnosis['technician_name']}</p>
            </div>
            
            <div class="section {'urgent' if result['urgency_level'] in ['긴급', 'critical'] else 'warning' if result['urgency_level'] in ['주의', 'warning'] else 'normal'}">
                <h2>🎯 진단 결과</h2>
                <p><strong>냉매 수준:</strong> {result['refrigerant_level']}</p>
                <p><strong>긴급도:</strong> {result['urgency_level']}</p>
                <p><strong>신뢰도:</strong> {result['confidence_score']:.1%}</p>
                <p><strong>위험도 점수:</strong> {result['total_score']}/100</p>
            </div>
            
            <div class="section">
                <h2>🔧 권장 조치사항</h2>
                <p>{result['recommended_action']}</p>
            </div>
            
            <div class="section">
                <h2>👁️ 현장 관찰</h2>
                <p><strong>냉각 성능:</strong> {observations['cooling_performance']}</p>
                <p><strong>압축기 온도:</strong> {observations['compressor_temperature']}</p>
                <p><strong>결빙 상태:</strong> {observations['frost_formation']}</p>
                <p><strong>운전 패턴:</strong> {observations['cycling_frequency']}</p>
            </div>
            
            <div class="section">
                <h2>🔍 상세 분석</h2>
                {'<br>'.join(f'• {detail}' for detail in result['analysis_details'])}
            </div>
        </body>
        </html>
        """
        
        # 리포트 파일 저장
        report_filename = f"냉매진단리포트_{diagnosis['customer_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        os.makedirs("refrigerant_reports", exist_ok=True)
        report_path = f"refrigerant_reports/{report_filename}"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        st.success(f"📄 리포트가 생성되었습니다: {report_filename}")
        
        # 다운로드 링크
        with open(report_path, 'r', encoding='utf-8') as f:
            st.download_button(
                label="📥 리포트 다운로드",
                data=f.read(),
                file_name=report_filename,
                mime='text/html'
            )
    
    def show_diagnosis_history(self):
        """진단 이력 표시"""
        st.subheader("📚 냉매 진단 이력")
        
        conn = sqlite3.connect('refrigerant_diagnosis.db')
        
        try:
            history = pd.read_sql_query('''
                SELECT customer_name, equipment_id, refrigerant_level, 
                       urgency_level, confidence_score, diagnosis_time
                FROM refrigerant_diagnoses
                ORDER BY diagnosis_time DESC
                LIMIT 50
            ''', conn)
            
            if len(history) > 0:
                # 통계 요약
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_diagnoses = len(history)
                    st.metric("총 진단 수", total_diagnoses)
                
                with col2:
                    urgent_count = len(history[history['urgency_level'].isin(['긴급', 'critical'])])
                    st.metric("긴급 케이스", urgent_count, delta=f"{urgent_count/total_diagnoses:.1%}")
                
                with col3:
                    avg_confidence = history['confidence_score'].mean()
                    st.metric("평균 신뢰도", f"{avg_confidence:.1%}")
                
                # 이력 테이블
                st.dataframe(history, use_container_width=True)
                
                # 진단 결과 분포
                fig = px.pie(history, names='refrigerant_level', 
                           title="냉매 상태 분포")
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("진단 이력이 없습니다.")
                
        except Exception as e:
            st.error(f"이력 조회 실패: {e}")
        finally:
            conn.close()
    
    def run(self):
        """메인 애플리케이션 실행"""
        # 사이드바
        with st.sidebar:
            st.title("🧊 냉매 진단 시스템")
            
            menu = st.selectbox(
                "메뉴 선택",
                ["🎯 새 진단", "📚 진단 이력", "📊 통계 분석", "⚙️ 설정"]
            )
            
            # 빠른 정보
            st.markdown("---")
            st.markdown("### 🚨 긴급 체크리스트")
            st.markdown("""
            **즉시 확인사항:**
            - ❄️ 냉각 성능 급격히 저하
            - 🔥 압축기 과열 (만지기 어려움)
            - 🧊 증발기 과도한 결빙
            - ⚡ 전력 소모 급증
            - 🔊 평소와 다른 소음
            """)
            
            st.markdown("---")
            st.markdown("### 📞 긴급 연락처")
            st.markdown("""
            **기술 지원**: 1588-0000  
            **응급 수리**: 010-0000-0000  
            **본사**: 02-0000-0000
            """)
        
        # 메인 콘텐츠
        if menu == "🎯 새 진단":
            self.show_main_interface()
        elif menu == "📚 진단 이력":
            self.show_diagnosis_history()
        elif menu == "📊 통계 분석":
            st.write("통계 분석 기능은 개발 중입니다.")
        elif menu == "⚙️ 설정":
            st.write("설정 기능은 개발 중입니다.")

# 메인 실행
if __name__ == "__main__":
    detector = RefrigerantLeakDetector()
    detector.run()
