# reliable_report_generator.py - 안정적인 리포트 생성기
import os
from datetime import datetime

def create_reliable_text_report(data, filename):
    """안정적인 텍스트 리포트 생성"""
    try:
        print(f"📄 텍스트 리포트 생성 시작: {filename}")
        
        # 안전한 데이터 추출
        customer_name = str(data.get('customer_name', '고객명'))
        equipment_type = str(data.get('equipment_type', '장비유형'))
        equipment_id = str(data.get('equipment_id', '장비ID'))
        technician_name = str(data.get('technician_name', '기술자'))
        diagnosis = str(data.get('diagnosis', '진단결과'))
        
        # 신뢰도 처리
        try:
            confidence = float(data.get('confidence', 0.8))
            confidence_percent = int(confidence * 100)
        except (ValueError, TypeError):
            confidence_percent = 80
        
        # 현재 시간
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')
        
        content = f"""
===========================================
        압축기 진단 리포트
===========================================

생성일시: {current_time}
리포트 ID: RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}

-------------------------------------------
📋 기본 정보
-------------------------------------------
고객명: {customer_name}
장비 유형: {equipment_type}
장비 ID: {equipment_id}
담당 기술자: {technician_name}

-------------------------------------------
🔍 진단 결과
-------------------------------------------
진단 결과: {diagnosis}
신뢰도: {confidence_percent}%

상태 평가:
"""
        
        # 진단 결과에 따른 상태 메시지
        if "정상" in diagnosis:
            content += """✅ 정상 상태
   - 장비가 정상적으로 작동하고 있습니다
   - 현재 상태를 유지하시기 바랍니다
"""
        elif "주의" in diagnosis:
            content += """⚠️ 주의 필요
   - 일부 이상 징후가 감지되었습니다
   - 정기 점검을 권장합니다
"""
        else:
            content += """🚨 이상 감지
   - 장비 이상이 확인되었습니다
   - 즉시 점검이 필요합니다
"""
        
        content += f"""
-------------------------------------------
💡 권장사항
-------------------------------------------
"""
        
        # 진단 결과별 권장사항
        if "정상" in diagnosis:
            recommendations = [
                "현재 상태를 유지하세요",
                "정기적인 점검을 계속하세요",
                "다음 진단 권장: 3개월 후",
                "운전 조건을 기록해 두세요"
            ]
        elif "주의" in diagnosis:
            recommendations = [
                "운전 조건을 점검하세요",
                "1-2주 내 재점검을 권장합니다",
                "부하를 줄여보세요",
                "전문가 상담을 받으세요"
            ]
        else:
            recommendations = [
                "즉시 운전을 중단하세요",
                "전문 기술자에게 연락하세요",
                "긴급 수리가 필요합니다",
                "안전 점검을 실시하세요"
            ]
        
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"
        
        content += f"""
-------------------------------------------
📞 긴급 연락처
-------------------------------------------
🆘 24시간 응급출동: 010-1234-5678
📞 기술 지원센터: 1588-0000
📧 이메일 문의: support@smartdiag.co.kr
🌐 웹사이트: www.smartdiag.co.kr

📍 본사 주소: 서울시 강남구 테헤란로 123
⏰ 고객센터 운영: 평일 09:00-18:00

-------------------------------------------
⚠️ 중요 안내사항
-------------------------------------------
• 본 진단 결과는 AI 기반 분석 결과입니다
• 정확한 진단을 위해서는 전문가 현장 점검이 필요합니다
• 긴급상황 시 즉시 운전을 중단하고 연락하세요
• 정기적인 점검으로 장비 수명을 연장할 수 있습니다

-------------------------------------------
© 2024 SmartDiag Solutions Co., Ltd.
AI 압축기 진단 시스템 v3.2
===========================================
"""
        
        # 파일 작성
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 텍스트 리포트 생성 완료: {filename}")
        print(f"📄 파일 크기: {os.path.getsize(filename)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 텍스트 리포트 생성 실패: {e}")
        print(f"오류 세부사항: {type(e).__name__}")
        return False

def create_simple_html_report(data, filename):
    """간단한 HTML 리포트 생성"""
    try:
        print(f"🌐 HTML 리포트 생성 시작: {filename}")
        
        # 안전한 데이터 추출
        customer_name = str(data.get('customer_name', '고객명'))
        equipment_type = str(data.get('equipment_type', '장비유형'))
        equipment_id = str(data.get('equipment_id', '장비ID'))
        technician_name = str(data.get('technician_name', '기술자'))
        diagnosis = str(data.get('diagnosis', '진단결과'))
        
        # 신뢰도 처리
        try:
            confidence = float(data.get('confidence', 0.8))
            confidence_percent = int(confidence * 100)
        except (ValueError, TypeError):
            confidence_percent = 80
        
        # 상태별 색상
        if "정상" in diagnosis:
            status_class = "normal"
            status_icon = "✅"
        elif "주의" in diagnosis:
            status_class = "caution"
            status_icon = "⚠️"
        else:
            status_class = "danger"
            status_icon = "🚨"
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>압축기 진단 리포트</title>
</head>
<body style="font-family: 'Malgun Gothic', Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; color: #000000;">
    
    <div style="max-width: 800px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); color: #000000;">
        
        <div style="text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="color: #007bff; margin: 0; font-size: 28px;">🔧 압축기 진단 리포트</h1>
            <p style="color: #666; margin: 5px 0;">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}</p>
            <p style="color: #666; margin: 5px 0;">리포트 ID: RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}</p>
        </div>
        
        <h2 style="color: #000000; font-size: 20px; margin: 20px 0;">📍 진단 정보</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                <h3 style="color: #000000; font-size: 14px; margin: 0 0 10px 0; font-weight: bold;">🏢 고객</h3>
                <p style="color: #000000; font-size: 16px; font-weight: bold; margin: 0;">{customer_name}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                <h3 style="color: #000000; font-size: 14px; margin: 0 0 10px 0; font-weight: bold;">🔧 장비</h3>
                <p style="color: #000000; font-size: 16px; font-weight: bold; margin: 0;">{equipment_type} - {equipment_id}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                <h3 style="color: #000000; font-size: 14px; margin: 0 0 10px 0; font-weight: bold;">👨‍🔧 기술자</h3>
                <p style="color: #000000; font-size: 16px; font-weight: bold; margin: 0;">{technician_name}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                <h3 style="color: #000000; font-size: 14px; margin: 0 0 10px 0; font-weight: bold;">📅 진단 시간</h3>
                <p style="color: #000000; font-size: 16px; font-weight: bold; margin: 0;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
        </div>
        
        <div style="text-align: center; padding: 20px; border-radius: 10px; margin: 30px 0; font-size: 24px; font-weight: bold; {'background: #d4edda; color: #155724; border: 2px solid #c3e6cb;' if '정상' in diagnosis else 'background: #fff3cd; color: #856404; border: 2px solid #ffeaa7;' if '주의' in diagnosis else 'background: #f8d7da; color: #721c24; border: 2px solid #f5c6cb;'}">
            {status_icon} {diagnosis} (신뢰도: {confidence_percent}%)
        </div>
        
        <h2 style="color: #000000; font-size: 20px; margin: 20px 0;">📈 분석 상세</h2>
        <p style="color: #000000; font-size: 14px;">현장에서 수집된 소음 데이터를 AI가 분석한 결과입니다.</p>
        
        <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; color: #000000;">
            <h3 style="color: #1976d2; margin-top: 0; font-weight: bold;">💡 권장사항</h3>
            <ol style="color: #000000; margin: 10px 0; padding-left: 20px;">"""
        
        # 권장사항 추가
        if "정상" in diagnosis:
            recommendations = [
                "현재 상태를 유지하세요",
                "정기적인 점검을 계속하세요",
                "다음 진단 권장: 3개월 후",
                "운전 조건을 기록해 두세요"
            ]
        elif "주의" in diagnosis:
            recommendations = [
                "운전 조건을 점검하세요",
                "1-2주 내 재점검을 권장합니다",
                "부하를 줄여보세요",
                "전문가 상담을 받으세요"
            ]
        else:
            recommendations = [
                "즉시 운전을 중단하세요",
                "전문 기술자에게 연락하세요",
                "긴급 수리가 필요합니다",
                "안전 점검을 실시하세요"
            ]
        
        for rec in recommendations:
            html_content += f'                <li style="color: #000000; margin: 8px 0;">{rec}</li>\n'
        
        html_content += f"""            </ol>
        </div>
        
        <div style="background: #fff3e0; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #ff9800; color: #000000;">
            <h3 style="color: #e65100; margin-top: 0; font-weight: bold;">📞 긴급 연락처</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0;">
                <div style="background: white; padding: 10px; border-radius: 5px; text-align: center; color: #000000;">
                    <strong style="color: #e65100;">🆘 응급출동</strong><br>
                    <span style="color: #000000;">010-1234-5678</span>
                </div>
                <div style="background: white; padding: 10px; border-radius: 5px; text-align: center; color: #000000;">
                    <strong style="color: #e65100;">📞 기술지원</strong><br>
                    <span style="color: #000000;">1588-0000</span>
                </div>
                <div style="background: white; padding: 10px; border-radius: 5px; text-align: center; color: #000000;">
                    <strong style="color: #e65100;">📧 이메일</strong><br>
                    <span style="color: #000000;">support@smartdiag.co.kr</span>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
            <p style="color: #6c757d; font-size: 12px; margin: 5px 0;"><strong style="color: #6c757d;">⚠️ 중요:</strong> 본 진단 결과는 AI 기반 분석 결과입니다.</p>
            <p style="color: #6c757d; font-size: 12px; margin: 5px 0;">© 2024 SmartDiag Solutions Co., Ltd.</p>
        </div>
        
    </div>
    
</body>
</html>"""
        
        # 파일 작성
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML 리포트 생성 완료: {filename}")
        print(f"📄 파일 크기: {os.path.getsize(filename)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML 리포트 생성 실패: {e}")
        print(f"오류 세부사항: {type(e).__name__}")
        return False

def generate_offline_report(data, preferred_format="html"):
    """오프라인 리포트 생성 (여러 형식 지원)"""
    print(f"🔧 오프라인 리포트 생성 시작 (형식: {preferred_format})")
    
    # 안전한 파일명 생성
    try:
        customer_name = str(data.get('customer_name', '고객')).replace('/', '_').replace('\\', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = []
        
        # 1. HTML 리포트 시도
        if preferred_format == "html" or preferred_format == "all":
            html_filename = f"진단리포트_{customer_name}_{timestamp}.html"
            if create_simple_html_report(data, html_filename):
                results.append(("html", html_filename))
        
        # 2. 텍스트 리포트 시도 (백업)
        if preferred_format == "txt" or preferred_format == "all" or not results:
            txt_filename = f"진단리포트_{customer_name}_{timestamp}.txt"
            if create_reliable_text_report(data, txt_filename):
                results.append(("txt", txt_filename))
        
        if results:
            print(f"✅ 오프라인 리포트 생성 성공: {len(results)}개 파일")
            return results
        else:
            print("❌ 모든 리포트 형식 생성 실패")
            return []
            
    except Exception as e:
        print(f"❌ 오프라인 리포트 생성 중 오류: {e}")
        return []

# 테스트 함수
def test_reliable_generator():
    """안정적인 생성기 테스트"""
    print("🔧 안정적인 리포트 생성기 테스트")
    print("=" * 50)
    
    test_data = {
        'customer_name': '테스트 고객',
        'equipment_type': '압축기',
        'equipment_id': 'TEST-001',
        'technician_name': '김진단',
        'diagnosis': '정상',
        'confidence': 0.95
    }
    
    results = generate_offline_report(test_data, "all")
    
    print(f"\n📊 테스트 결과: {len(results)}개 파일 생성")
    for format_type, filename in results:
        print(f"  - {format_type.upper()}: {filename}")
    
    return len(results) > 0

if __name__ == "__main__":
    test_reliable_generator()
