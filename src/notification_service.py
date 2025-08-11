# notification_service.py - 알림 서비스 (카카오톡, 문자, 이메일)
import requests
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import os
from datetime import datetime
from typing import Optional

class NotificationService:
    def __init__(self):
        # 카카오톡 알림톡 설정 (실제 서비스용)
        self.kakao_api_key = os.getenv("KAKAO_API_KEY", "")
        self.kakao_sender_key = os.getenv("KAKAO_SENDER_KEY", "")
        
        # SMS 서비스 설정 (예: 네이버 클라우드, AWS SNS 등)
        self.sms_api_key = os.getenv("SMS_API_KEY", "")
        self.sms_secret = os.getenv("SMS_SECRET", "")
        
        # 이메일 서비스 설정
        self.email_smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.email_smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
    
    def send_kakao_message(self, phone_number: str, customer_name: str, diagnosis_result: dict) -> bool:
        """카카오톡 알림톡으로 진단 결과 전송"""
        try:
            # 카카오톡 알림톡 메시지 템플릿
            message_template = f"""
🔧 압축기 진단 결과 알림

안녕하세요, {customer_name} 사장님!
방금 전 진행한 장비 진단이 완료되었습니다.

📊 진단 결과
• 장비: {diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}
• 결과: {diagnosis_result.get('diagnosis')}
• 신뢰도: {int(diagnosis_result.get('confidence', 0) * 100)}%
• 진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 권장사항:
{self._format_recommendations(diagnosis_result.get('recommendations', []))}

상세한 리포트는 별도로 전달드리겠습니다.
추가 문의사항이 있으시면 연락 부탁드립니다.

감사합니다.
- 압축기 진단 서비스팀
            """
            
            # 실제 카카오톡 알림톡 API 호출 (시뮬레이션)
            if self._is_demo_mode():
                print(f"[DEMO] 카카오톡 메시지 전송 ({phone_number})")
                print(message_template)
                return True
            
            # 실제 API 호출 코드 (카카오톡 비즈니스 API)
            url = "https://api.kakaowork.com/v1/messages.send"
            headers = {
                "Authorization": f"Bearer {self.kakao_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "conversation_id": phone_number,
                "text": message_template,
                "blocks": [
                    {
                        "type": "text",
                        "text": message_template
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"카카오톡 전송 오류: {e}")
            return False
    
    def send_sms_message(self, phone_number: str, customer_name: str, diagnosis_result: dict) -> bool:
        """SMS로 진단 결과 전송"""
        try:
            # SMS 메시지 (글자 수 제한 고려)
            diagnosis = diagnosis_result.get('diagnosis', '알 수 없음')
            confidence = int(diagnosis_result.get('confidence', 0) * 100)
            equipment = f"{diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}"
            
            sms_message = f"""
[압축기 진단 완료]

{customer_name} 사장님, 
{equipment} 진단이 완료되었습니다.

결과: {diagnosis} ({confidence}%)
시간: {datetime.now().strftime('%m/%d %H:%M')}

상세 리포트는 별도 전달드립니다.

-압축기진단팀
            """.strip()
            
            # 글자 수 제한 (SMS 80자, LMS 2000자)
            if len(sms_message) > 80:
                # LMS로 전송
                return self._send_lms(phone_number, sms_message)
            else:
                # SMS로 전송
                return self._send_sms(phone_number, sms_message)
                
        except Exception as e:
            print(f"SMS 전송 오류: {e}")
            return False
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """SMS 전송 (실제 구현)"""
        if self._is_demo_mode():
            print(f"[DEMO] SMS 전송 ({phone_number})")
            print(message)
            return True
        
        # 실제 SMS API 호출 (예: 네이버 클라우드 플랫폼)
        try:
            url = "https://sens.apigw.ntruss.com/sms/v2/services/{serviceId}/messages"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "x-ncp-apigw-timestamp": str(int(datetime.now().timestamp() * 1000)),
                "x-ncp-iam-access-key": self.sms_api_key,
                "x-ncp-apigw-signature-v2": self._make_signature()  # 서명 생성 필요
            }
            
            payload = {
                "type": "SMS",
                "contentType": "COMM",
                "from": "01012345678",  # 발신번호 (사전 등록 필요)
                "content": message,
                "messages": [
                    {
                        "to": phone_number
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 202  # SMS는 202 반환
            
        except Exception as e:
            print(f"실제 SMS 전송 오류: {e}")
            return False
    
    def _send_lms(self, phone_number: str, message: str) -> bool:
        """LMS 전송 (긴 문자)"""
        if self._is_demo_mode():
            print(f"[DEMO] LMS 전송 ({phone_number})")
            print(message)
            return True
        
        # LMS 전송 로직 (SMS와 유사하지만 type을 LMS로 설정)
        return self._send_sms(phone_number, message)  # 실제로는 type: "LMS"
    
    def send_email_report(self, email: str, customer_name: str, diagnosis_result: dict, 
                         pdf_path: Optional[str] = None) -> bool:
        """이메일로 진단 리포트 전송"""
        try:
            # 이메일 메시지 생성
            msg = MimeMultipart()
            msg['From'] = self.email_address
            msg['To'] = email
            msg['Subject'] = f"[압축기 진단] {customer_name} - 진단 리포트"
            
            # 이메일 본문
            body = self._create_email_body(customer_name, diagnosis_result)
            msg.attach(MimeText(body, 'html'))
            
            # PDF 첨부 파일
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as attachment:
                    part = MimeBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_path)}'
                )
                msg.attach(part)
            
            # 이메일 전송
            if self._is_demo_mode():
                print(f"[DEMO] 이메일 전송 ({email})")
                print(body)
                return True
            
            # 실제 이메일 전송
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"이메일 전송 오류: {e}")
            return False
    
    def _create_email_body(self, customer_name: str, diagnosis_result: dict) -> str:
        """이메일 본문 HTML 생성"""
        diagnosis = diagnosis_result.get('diagnosis', '알 수 없음')
        confidence = int(diagnosis_result.get('confidence', 0) * 100)
        equipment = f"{diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}"
        
        # 상태에 따른 색상
        status_colors = {
            '정상': '#4CAF50',
            '주의 필요': '#FF9800',
            '이상 감지': '#F44336'
        }
        
        status_color = status_colors.get(diagnosis, '#757575')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .result-box {{ 
                    background-color: {status_color}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    text-align: center; 
                    margin: 20px 0; 
                }}
                .info-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                .info-table th, .info-table td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                .info-table th {{ background-color: #f8f9fa; }}
                .recommendations {{ background-color: #e3f2fd; padding: 15px; border-radius: 8px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔧 압축기 진단 리포트</h1>
            </div>
            
            <div class="content">
                <p>안녕하세요, <strong>{customer_name}</strong> 사장님!</p>
                <p>요청하신 장비 진단이 완료되어 결과를 전달드립니다.</p>
                
                <div class="result-box">
                    <h2>진단 결과: {diagnosis}</h2>
                    <p>신뢰도: {confidence}%</p>
                </div>
                
                <table class="info-table">
                    <tr><th>진단 항목</th><th>내용</th></tr>
                    <tr><td>장비 정보</td><td>{equipment}</td></tr>
                    <tr><td>진단 시간</td><td>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</td></tr>
                    <tr><td>진단자</td><td>{diagnosis_result.get('technician_name', 'N/A')}</td></tr>
                </table>
                
                <div class="recommendations">
                    <h3>💡 권장사항</h3>
                    {self._format_recommendations_html(diagnosis_result.get('recommendations', []))}
                </div>
                
                <p>상세한 기술 정보와 분석 차트는 첨부된 PDF 리포트를 참조해 주세요.</p>
                <p>추가 문의사항이 있으시면 언제든 연락 부탁드립니다.</p>
            </div>
            
            <div class="footer">
                <p>© 2024 압축기 진단 서비스 | 문의: support@compressor-ai.com | 전화: 1588-0000</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _format_recommendations(self, recommendations: list) -> str:
        """권장사항을 텍스트로 포맷팅"""
        if not recommendations:
            return "특별한 권장사항이 없습니다."
        
        formatted = []
        for i, rec in enumerate(recommendations[:3], 1):  # 최대 3개만
            formatted.append(f"{i}. {rec}")
        
        return "\n".join(formatted)
    
    def _format_recommendations_html(self, recommendations: list) -> str:
        """권장사항을 HTML로 포맷팅"""
        if not recommendations:
            return "<p>특별한 권장사항이 없습니다.</p>"
        
        html_items = []
        for rec in recommendations:
            html_items.append(f"<li>{rec}</li>")
        
        return f"<ul>{''.join(html_items)}</ul>"
    
    def _make_signature(self) -> str:
        """API 서명 생성 (SMS 서비스용)"""
        # 실제 구현에서는 HMAC-SHA256을 사용하여 서명 생성
        import hmac
        import hashlib
        import base64
        
        # 네이버 클라우드 플랫폼 SMS API 서명 생성 예시
        timestamp = str(int(datetime.now().timestamp() * 1000))
        access_key = self.sms_api_key
        secret_key = self.sms_secret
        
        message = f"POST /sms/v2/services/ncp:sms:kr:123456789:service_id/messages\n{timestamp}\n{access_key}"
        
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        
        return signature
    
    def _is_demo_mode(self) -> bool:
        """데모 모드 확인 (실제 API 키가 없는 경우)"""
        return not all([self.kakao_api_key, self.sms_api_key, self.email_address])
    
    def send_diagnosis_notification(self, contact_info: dict, diagnosis_result: dict, 
                                  pdf_path: Optional[str] = None) -> dict:
        """통합 알림 전송"""
        results = {
            "kakao": False,
            "sms": False,
            "email": False
        }
        
        customer_name = contact_info.get('customer_name', '고객')
        
        # 카카오톡 전송
        if contact_info.get('phone'):
            results["kakao"] = self.send_kakao_message(
                contact_info['phone'], customer_name, diagnosis_result
            )
        
        # SMS 전송
        if contact_info.get('phone'):
            results["sms"] = self.send_sms_message(
                contact_info['phone'], customer_name, diagnosis_result
            )
        
        # 이메일 전송
        if contact_info.get('email'):
            results["email"] = self.send_email_report(
                contact_info['email'], customer_name, diagnosis_result, pdf_path
            )
        
        return results

# 사용 예시
def test_notification_service():
    """알림 서비스 테스트"""
    service = NotificationService()
    
    # 테스트 데이터
    contact_info = {
        'customer_name': 'A수산',
        'phone': '010-1234-5678',
        'email': 'test@example.com'
    }
    
    diagnosis_result = {
        'equipment_type': '냉동고',
        'equipment_id': '1번 냉동고',
        'diagnosis': '정상',
        'confidence': 0.95,
        'technician_name': '김기술',
        'recommendations': [
            '현재 장비 상태가 양호합니다',
            '정기적인 점검을 유지하세요',
            '3개월 후 재점검을 권장합니다'
        ]
    }
    
    # 통합 알림 전송
    results = service.send_diagnosis_notification(contact_info, diagnosis_result)
    print("알림 전송 결과:", results)

if __name__ == "__main__":
    test_notification_service()
import requests
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import os
from datetime import datetime
from typing import Optional

class NotificationService:
    def __init__(self):
        # 카카오톡 알림톡 설정 (실제 서비스용)
        self.kakao_api_key = os.getenv("KAKAO_API_KEY", "")
        self.kakao_sender_key = os.getenv("KAKAO_SENDER_KEY", "")
        
        # SMS 서비스 설정 (예: 네이버 클라우드, AWS SNS 등)
        self.sms_api_key = os.getenv("SMS_API_KEY", "")
        self.sms_secret = os.getenv("SMS_SECRET", "")
        
        # 이메일 서비스 설정
        self.email_smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.email_smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
    
    def send_kakao_message(self, phone_number: str, customer_name: str, diagnosis_result: dict) -> bool:
        """카카오톡 알림톡으로 진단 결과 전송"""
        try:
            # 카카오톡 알림톡 메시지 템플릿
            message_template = f"""
🔧 압축기 진단 결과 알림

안녕하세요, {customer_name} 사장님!
방금 전 진행한 장비 진단이 완료되었습니다.

📊 진단 결과
• 장비: {diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}
• 결과: {diagnosis_result.get('diagnosis')}
• 신뢰도: {int(diagnosis_result.get('confidence', 0) * 100)}%
• 진단 시간: {datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 권장사항:
{self._format_recommendations(diagnosis_result.get('recommendations', []))}

상세한 리포트는 별도로 전달드리겠습니다.
추가 문의사항이 있으시면 연락 부탁드립니다.

감사합니다.
- 압축기 진단 서비스팀
            """
            
            # 실제 카카오톡 알림톡 API 호출 (시뮬레이션)
            if self._is_demo_mode():
                print(f"[DEMO] 카카오톡 메시지 전송 ({phone_number})")
                print(message_template)
                return True
            
            # 실제 API 호출 코드 (카카오톡 비즈니스 API)
            url = "https://api.kakaowork.com/v1/messages.send"
            headers = {
                "Authorization": f"Bearer {self.kakao_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "conversation_id": phone_number,
                "text": message_template,
                "blocks": [
                    {
                        "type": "text",
                        "text": message_template
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 200
            
        except Exception as e:
            print(f"카카오톡 전송 오류: {e}")
            return False
    
    def send_sms_message(self, phone_number: str, customer_name: str, diagnosis_result: dict) -> bool:
        """SMS로 진단 결과 전송"""
        try:
            # SMS 메시지 (글자 수 제한 고려)
            diagnosis = diagnosis_result.get('diagnosis', '알 수 없음')
            confidence = int(diagnosis_result.get('confidence', 0) * 100)
            equipment = f"{diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}"
            
            sms_message = f"""
[압축기 진단 완료]

{customer_name} 사장님, 
{equipment} 진단이 완료되었습니다.

결과: {diagnosis} ({confidence}%)
시간: {datetime.now().strftime('%m/%d %H:%M')}

상세 리포트는 별도 전달드립니다.

-압축기진단팀
            """.strip()
            
            # 글자 수 제한 (SMS 80자, LMS 2000자)
            if len(sms_message) > 80:
                # LMS로 전송
                return self._send_lms(phone_number, sms_message)
            else:
                # SMS로 전송
                return self._send_sms(phone_number, sms_message)
                
        except Exception as e:
            print(f"SMS 전송 오류: {e}")
            return False
    
    def _send_sms(self, phone_number: str, message: str) -> bool:
        """SMS 전송 (실제 구현)"""
        if self._is_demo_mode():
            print(f"[DEMO] SMS 전송 ({phone_number})")
            print(message)
            return True
        
        # 실제 SMS API 호출 (예: 네이버 클라우드 플랫폼)
        try:
            url = "https://sens.apigw.ntruss.com/sms/v2/services/{serviceId}/messages"
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "x-ncp-apigw-timestamp": str(int(datetime.now().timestamp() * 1000)),
                "x-ncp-iam-access-key": self.sms_api_key,
                "x-ncp-apigw-signature-v2": self._make_signature()  # 서명 생성 필요
            }
            
            payload = {
                "type": "SMS",
                "contentType": "COMM",
                "from": "01012345678",  # 발신번호 (사전 등록 필요)
                "content": message,
                "messages": [
                    {
                        "to": phone_number
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 202  # SMS는 202 반환
            
        except Exception as e:
            print(f"실제 SMS 전송 오류: {e}")
            return False
    
    def _send_lms(self, phone_number: str, message: str) -> bool:
        """LMS 전송 (긴 문자)"""
        if self._is_demo_mode():
            print(f"[DEMO] LMS 전송 ({phone_number})")
            print(message)
            return True
        
        # LMS 전송 로직 (SMS와 유사하지만 type을 LMS로 설정)
        return self._send_sms(phone_number, message)  # 실제로는 type: "LMS"
    
    def send_email_report(self, email: str, customer_name: str, diagnosis_result: dict, 
                         pdf_path: Optional[str] = None) -> bool:
        """이메일로 진단 리포트 전송"""
        try:
            # 이메일 메시지 생성
            msg = MimeMultipart()
            msg['From'] = self.email_address
            msg['To'] = email
            msg['Subject'] = f"[압축기 진단] {customer_name} - 진단 리포트"
            
            # 이메일 본문
            body = self._create_email_body(customer_name, diagnosis_result)
            msg.attach(MimeText(body, 'html'))
            
            # PDF 첨부 파일
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as attachment:
                    part = MimeBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_path)}'
                )
                msg.attach(part)
            
            # 이메일 전송
            if self._is_demo_mode():
                print(f"[DEMO] 이메일 전송 ({email})")
                print(body)
                return True
            
            # 실제 이메일 전송
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, email, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"이메일 전송 오류: {e}")
            return False
    
    def _create_email_body(self, customer_name: str, diagnosis_result: dict) -> str:
        """이메일 본문 HTML 생성"""
        diagnosis = diagnosis_result.get('diagnosis', '알 수 없음')
        confidence = int(diagnosis_result.get('confidence', 0) * 100)
        equipment = f"{diagnosis_result.get('equipment_type')} - {diagnosis_result.get('equipment_id')}"
        
        # 상태에 따른 색상
        status_colors = {
            '정상': '#4CAF50',
            '주의 필요': '#FF9800',
            '이상 감지': '#F44336'
        }
        
        status_color = status_colors.get(diagnosis, '#757575')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .result-box {{ 
                    background-color: {status_color}; 
                    color: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    text-align: center; 
                    margin: 20px 0; 
                }}
                .info-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                .info-table th, .info-table td {{ 
                    border: 1px solid #ddd; 
                    padding: 12px; 
                    text-align: left; 
                }}
                .info-table th {{ background-color: #f8f9fa; }}
                .recommendations {{ background-color: #e3f2fd; padding: 15px; border-radius: 8px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔧 압축기 진단 리포트</h1>
            </div>
            
            <div class="content">
                <p>안녕하세요, <strong>{customer_name}</strong> 사장님!</p>
                <p>요청하신 장비 진단이 완료되어 결과를 전달드립니다.</p>
                
                <div class="result-box">
                    <h2>진단 결과: {diagnosis}</h2>
                    <p>신뢰도: {confidence}%</p>
                </div>
                
                <table class="info-table">
                    <tr><th>진단 항목</th><th>내용</th></tr>
                    <tr><td>장비 정보</td><td>{equipment}</td></tr>
                    <tr><td>진단 시간</td><td>{datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</td></tr>
                    <tr><td>진단자</td><td>{diagnosis_result.get('technician_name', 'N/A')}</td></tr>
                </table>
                
                <div class="recommendations">
                    <h3>💡 권장사항</h3>
                    {self._format_recommendations_html(diagnosis_result.get('recommendations', []))}
                </div>
                
                <p>상세한 기술 정보와 분석 차트는 첨부된 PDF 리포트를 참조해 주세요.</p>
                <p>추가 문의사항이 있으시면 언제든 연락 부탁드립니다.</p>
            </div>
            
            <div class="footer">
                <p>© 2024 압축기 진단 서비스 | 문의: support@compressor-ai.com | 전화: 1588-0000</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _format_recommendations(self, recommendations: list) -> str:
        """권장사항을 텍스트로 포맷팅"""
        if not recommendations:
            return "특별한 권장사항이 없습니다."
        
        formatted = []
        for i, rec in enumerate(recommendations[:3], 1):  # 최대 3개만
            formatted.append(f"{i}. {rec}")
        
        return "\n".join(formatted)
    
    def _format_recommendations_html(self, recommendations: list) -> str:
        """권장사항을 HTML로 포맷팅"""
        if not recommendations:
            return "<p>특별한 권장사항이 없습니다.</p>"
        
        html_items = []
        for rec in recommendations:
            html_items.append(f"<li>{rec}</li>")
        
        return f"<ul>{''.join(html_items)}</ul>"
    
    def _make_signature(self) -> str:
        """API 서명 생성 (SMS 서비스용)"""
        # 실제 구현에서는 HMAC-SHA256을 사용하여 서명 생성
        import hmac
        import hashlib
        import base64
        
        # 네이버 클라우드 플랫폼 SMS API 서명 생성 예시
        timestamp = str(int(datetime.now().timestamp() * 1000))
        access_key = self.sms_api_key
        secret_key = self.sms_secret
        
        message = f"POST /sms/v2/services/ncp:sms:kr:123456789:service_id/messages\n{timestamp}\n{access_key}"
        
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        
        return signature
    
    def _is_demo_mode(self) -> bool:
        """데모 모드 확인 (실제 API 키가 없는 경우)"""
        return not all([self.kakao_api_key, self.sms_api_key, self.email_address])
    
    def send_diagnosis_notification(self, contact_info: dict, diagnosis_result: dict, 
                                  pdf_path: Optional[str] = None) -> dict:
        """통합 알림 전송"""
        results = {
            "kakao": False,
            "sms": False,
            "email": False
        }
        
        customer_name = contact_info.get('customer_name', '고객')
        
        # 카카오톡 전송
        if contact_info.get('phone'):
            results["kakao"] = self.send_kakao_message(
                contact_info['phone'], customer_name, diagnosis_result
            )
        
        # SMS 전송
        if contact_info.get('phone'):
            results["sms"] = self.send_sms_message(
                contact_info['phone'], customer_name, diagnosis_result
            )
        
        # 이메일 전송
        if contact_info.get('email'):
            results["email"] = self.send_email_report(
                contact_info['email'], customer_name, diagnosis_result, pdf_path
            )
        
        return results

# 사용 예시
def test_notification_service():
    """알림 서비스 테스트"""
    service = NotificationService()
    
    # 테스트 데이터
    contact_info = {
        'customer_name': 'A수산',
        'phone': '010-1234-5678',
        'email': 'test@example.com'
    }
    
    diagnosis_result = {
        'equipment_type': '냉동고',
        'equipment_id': '1번 냉동고',
        'diagnosis': '정상',
        'confidence': 0.95,
        'technician_name': '김기술',
        'recommendations': [
            '현재 장비 상태가 양호합니다',
            '정기적인 점검을 유지하세요',
            '3개월 후 재점검을 권장합니다'
        ]
    }
    
    # 통합 알림 전송
    results = service.send_diagnosis_notification(contact_info, diagnosis_result)
    print("알림 전송 결과:", results)

if __name__ == "__main__":
    test_notification_service()








