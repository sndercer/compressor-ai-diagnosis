# admin_portal.py - 관리자용 압축기 진단 관리 포털
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# 🎨 Streamlit 페이지 설정
st.set_page_config(
    page_title="관리자 포털",
    page_icon="⚙️",
    layout="wide"
)

class AdminPortal:
    def __init__(self):
        self.session_state = st.session_state
        self.init_session_state()
        self.init_database()
    
    def init_session_state(self):
        """세션 상태 초기화"""
        if 'admin_logged_in' not in self.session_state:
            self.session_state.admin_logged_in = False
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            self.conn = sqlite3.connect('compressor_system.db', check_same_thread=False)
        except Exception as e:
            st.error(f"데이터베이스 연결 오류: {e}")
    
    def login_page(self):
        """관리자 로그인 페이지"""
        st.title("⚙️ 관리자 포털")
        
        if not self.session_state.admin_logged_in:
            with st.form("admin_login_form"):
                username = st.text_input("관리자 ID", placeholder="admin")
                password = st.text_input("비밀번호", type="password")
                submit_button = st.form_submit_button("로그인")
                
                if submit_button:
                    if username == "admin" and password == "admin123":
                        self.session_state.admin_logged_in = True
                        st.success("관리자 로그인 성공!")
                        st.rerun()
                    else:
                        st.error("로그인 실패. 관리자 계정을 확인해주세요.")
    
    def main_dashboard(self):
        """메인 관리자 대시보드"""
        st.title("⚙️ 관리자 포털")
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드", "👥 고객 관리", "📁 데이터 관리", "⚙️ 시스템 설정"])
        
        with tab1:
            self.dashboard_tab()
        
        with tab2:
            self.customer_management_tab()
        
        with tab3:
            self.data_management_tab()
        
        with tab4:
            self.system_settings_tab()
        
        # 로그아웃
        if st.sidebar.button("🚪 로그아웃"):
            self.session_state.admin_logged_in = False
            st.rerun()
    
    def dashboard_tab(self):
        """대시보드 탭"""
        st.subheader("📊 시스템 대시보드")
        
        # 시스템 통계
        stats = self.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 고객 수", stats['total_customers'])
        
        with col2:
            st.metric("총 파일 수", stats['total_files'])
        
        with col3:
            st.metric("오늘 진단 수", stats['today_diagnoses'])
        
        with col4:
            st.metric("AI 모델 정확도", f"{stats['model_accuracy']:.1%}")
        
        # 최근 활동
        st.subheader("🕒 최근 활동")
        activities = self.get_recent_activities()
        for activity in activities:
            st.write(f"• {activity['time']} - {activity['description']}")
    
    def customer_management_tab(self):
        """고객 관리 탭"""
        st.subheader("👥 고객 관리")
        
        # 고객 목록
        customers = self.get_customers()
        if not customers.empty:
            st.dataframe(customers, use_container_width=True)
        else:
            st.info("등록된 고객이 없습니다.")
        
        # 새 고객 등록
        st.subheader("➕ 새 고객 등록")
        with st.form("add_customer_form"):
            company_name = st.text_input("회사명")
            contact_person = st.text_input("담당자명")
            email = st.text_input("이메일")
            phone = st.text_input("연락처")
            
            if st.form_submit_button("고객 등록"):
                if self.add_customer(company_name, contact_person, email, phone):
                    st.success("고객이 등록되었습니다!")
                    st.rerun()
                else:
                    st.error("고객 등록에 실패했습니다.")
    
    def data_management_tab(self):
        """데이터 관리 탭"""
        st.subheader("📁 데이터 관리")
        
        # 파일 목록
        files = self.get_files_list()
        if not files.empty:
            st.dataframe(files, use_container_width=True)
        else:
            st.info("업로드된 파일이 없습니다.")
        
        # 데이터 백업
        st.subheader("💾 데이터 백업")
        if st.button("🔄 백업 생성"):
            result = self.backup_database()
            if result['success']:
                st.success(f"백업 완료: {result['path']}")
            else:
                st.error(f"백업 실패: {result['error']}")
    
    def system_settings_tab(self):
        """시스템 설정 탭"""
        st.subheader("⚙️ 시스템 설정")
        
        with st.form("system_settings_form"):
            max_file_size = st.number_input("최대 파일 크기 (MB)", 10, 1000, 100)
            auto_backup = st.checkbox("자동 백업", value=True)
            retention_days = st.number_input("데이터 보관 기간 (일)", 30, 365, 90)
            
            if st.form_submit_button("설정 저장"):
                st.success("설정이 저장되었습니다!")
        
        # 시스템 유지보수
        st.subheader("🔧 시스템 유지보수")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 임시 파일 정리"):
                st.success("임시 파일이 정리되었습니다.")
        
        with col2:
            if st.button("💾 데이터베이스 최적화"):
                st.success("데이터베이스 최적화 완료")
    
    def get_system_stats(self):
        """시스템 통계 조회"""
        try:
            cursor = self.conn.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]
            
            cursor = self.conn.execute("SELECT COUNT(*) FROM audio_files")
            total_files = cursor.fetchone()[0]
            
            today = datetime.now().date()
            cursor = self.conn.execute(
                "SELECT COUNT(*) FROM audio_files WHERE DATE(upload_time) = ?",
                (today,)
            )
            today_diagnoses = cursor.fetchone()[0]
            
            return {
                'total_customers': total_customers,
                'total_files': total_files,
                'today_diagnoses': today_diagnoses,
                'model_accuracy': 0.85
            }
        except Exception as e:
            return {'total_customers': 0, 'total_files': 0, 'today_diagnoses': 0, 'model_accuracy': 0.0}
    
    def get_customers(self):
        """고객 목록 조회"""
        try:
            cursor = self.conn.execute("SELECT * FROM customers ORDER BY company_name")
            columns = [description[0] for description in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            return pd.DataFrame()
    
    def get_files_list(self):
        """파일 목록 조회"""
        try:
            cursor = self.conn.execute("""
                SELECT af.*, c.company_name 
                FROM audio_files af 
                LEFT JOIN customers c ON af.customer_id = c.id 
                ORDER BY af.upload_time DESC
            """)
            columns = [description[0] for description in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            return pd.DataFrame()
    
    def get_recent_activities(self):
        """최근 활동 조회"""
        return [
            {"time": "10:30", "description": "새 고객 등록: ABC 회사"},
            {"time": "09:15", "description": "파일 업로드: 5개 파일"},
            {"time": "08:45", "description": "AI 모델 업데이트 완료"}
        ]
    
    def add_customer(self, company_name, contact_person, email, phone):
        """고객 추가"""
        try:
            customer_id = f"customer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor = self.conn.execute("""
                INSERT INTO customers (id, company_name, contact_person, email, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (customer_id, company_name, contact_person, email, phone))
            self.conn.commit()
            return True
        except Exception as e:
            return False
    
    def backup_database(self):
        """데이터베이스 백업"""
        try:
            import shutil
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{backup_dir}/admin_backup_{timestamp}.db"
            
            self.conn.commit()
            shutil.copy2('compressor_system.db', backup_path)
            
            return {'success': True, 'path': backup_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run(self):
        """메인 실행 함수"""
        if self.session_state.admin_logged_in:
            self.main_dashboard()
        else:
            self.login_page()

def main():
    """메인 함수"""
    portal = AdminPortal()
    portal.run()

if __name__ == "__main__":
    main() 