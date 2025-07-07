# config.py - src 폴더에 새로 만들 파일
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# .env 파일 로드
load_dotenv()

class DatabaseConfig:
    def __init__(self):
        # Supabase 설정
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        self.SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
        self.USE_LOCAL_DB = os.getenv('USE_LOCAL_DB', 'True').lower() == 'true'
        
        print(f"🔧 데이터베이스 설정: {'로컬 SQLite' if self.USE_LOCAL_DB else 'Supabase 클라우드'}")
        
    def get_supabase_client(self) -> Client:
        """Supabase 클라이언트 반환"""
        if not self.SUPABASE_URL or not self.SUPABASE_ANON_KEY:
            raise ValueError("❌ Supabase 연결 정보가 없습니다. .env 파일을 확인하세요!")
        
        return create_client(self.SUPABASE_URL, self.SUPABASE_ANON_KEY)

# 전역 설정 인스턴스
config = DatabaseConfig()

# 연결 테스트 함수
def test_supabase_connection():
    """Supabase 연결 테스트"""
    try:
        supabase = config.get_supabase_client()
        
        # 간단한 쿼리로 연결 테스트
        result = supabase.table('customers').select('*').limit(1).execute()
        
        print("✅ Supabase 연결 성공!")
        print(f"📊 고객 데이터 확인: {len(result.data)}개 레코드")
        return True
        
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return False

if __name__ == "__main__":
    # 연결 테스트 실행
    test_supabase_connection()