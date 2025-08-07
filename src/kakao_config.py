# kakao_config.py - 카카오톡 로그인 설정
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 카카오톡 API 설정
KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "your-kakao-client-id")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "your-kakao-client-secret")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:8501/auth/kakao/callback")

# 카카오톡 로그인 설정 확인
def check_kakao_config():
    """카카오톡 설정 상태 확인"""
    config_status = {
        "client_id": KAKAO_CLIENT_ID != "your-kakao-client-id",
        "client_secret": KAKAO_CLIENT_SECRET != "your-kakao-client-secret",
        "redirect_uri": KAKAO_REDIRECT_URI != "http://localhost:8501/auth/kakao/callback"
    }
    
    return config_status

def get_kakao_auth_url():
    """카카오톡 로그인 URL 생성"""
    if KAKAO_CLIENT_ID == "your-kakao-client-id":
        return None, "카카오톡 Client ID가 설정되지 않았습니다."
    
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    return auth_url, None

def print_setup_instructions():
    """카카오톡 설정 안내 출력"""
    print("🔧 카카오톡 로그인 설정 방법:")
    print("=" * 50)
    print("1. 카카오 개발자 센터에서 애플리케이션 생성:")
    print("   https://developers.kakao.com/")
    print()
    print("2. 애플리케이션 생성 후 다음 정보를 확인:")
    print("   - JavaScript 키 (Client ID)")
    print("   - REST API 키 (Client Secret)")
    print()
    print("3. 플랫폼 설정에서 리다이렉트 URI 추가:")
    print("   http://localhost:8501/auth/kakao/callback")
    print()
    print("4. .env 파일에 다음 내용 추가:")
    print("   KAKAO_CLIENT_ID=your-javascript-key")
    print("   KAKAO_CLIENT_SECRET=your-rest-api-key")
    print("   KAKAO_REDIRECT_URI=http://localhost:8501/auth/kakao/callback")
    print()
    print("5. 동의항목 설정:")
    print("   - 닉네임 (profile_nickname)")
    print("   - 이메일 (account_email)")
    print()
    print("6. 앱 키 설정에서 JavaScript 키를 Client ID로 사용")
    print("=" * 50)

if __name__ == "__main__":
    print("🔍 카카오톡 설정 상태 확인:")
    config_status = check_kakao_config()
    
    for key, is_set in config_status.items():
        status = "✅ 설정됨" if is_set else "❌ 설정 필요"
        print(f"   {key}: {status}")
    
    if not all(config_status.values()):
        print("\n" + "=" * 50)
        print_setup_instructions()
    else:
        print("\n✅ 모든 카카오톡 설정이 완료되었습니다!")
        auth_url, error = get_kakao_auth_url()
        if auth_url:
            print(f"🔗 로그인 URL: {auth_url}")
        else:
            print(f"❌ 오류: {error}") 