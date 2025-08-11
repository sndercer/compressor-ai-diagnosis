# Streamlit Cloud 배포용 메인 진입점
# 이 파일은 Streamlit Cloud에서 자동으로 인식됩니다.

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 메인 앱 실행
from field_diagnosis_app import FieldDiagnosisApp

if __name__ == "__main__":
    app = FieldDiagnosisApp()
    app.run()
