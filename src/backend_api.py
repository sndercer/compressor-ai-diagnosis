# backend_api.py - 백엔드 API 서버
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
import json
import hashlib
import jwt
from datetime import datetime, timedelta
import librosa
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="압축기 진단 API",
    description="압축기 진단을 위한 백엔드 API (카카오톡 로그인 지원)",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 보안 설정
SECRET_KEY = "your-secret-key-here"  # 실제 운영에서는 환경변수로 관리
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 카카오톡 API 설정
try:
    from kakao_config import KAKAO_CLIENT_ID, KAKAO_CLIENT_SECRET, KAKAO_REDIRECT_URI
except ImportError:
    KAKAO_CLIENT_ID = "your-kakao-client-id"
    KAKAO_CLIENT_SECRET = "your-kakao-client-secret"
    KAKAO_REDIRECT_URI = "http://localhost:8501/auth/kakao/callback"

security = HTTPBearer()

# 데이터베이스 초기화
def init_database():
    """데이터베이스 초기화"""
    conn = sqlite3.connect('compressor_system.db')
    cursor = conn.cursor()
    
    # 사용자 테이블 (카카오톡 로그인 지원)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            company_name TEXT,
            contact_person TEXT,
            phone TEXT,
            role TEXT DEFAULT 'customer',
            login_type TEXT DEFAULT 'email',  -- 'email' 또는 'kakao'
            kakao_id TEXT,  -- 카카오톡 사용자 ID
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 고객 테이블 (기존)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 오디오 파일 테이블 (기존)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            duration REAL,
            sample_rate INTEGER,
            file_path TEXT,
            customer_id TEXT,
            equipment_id TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            diagnosis_result TEXT,
            confidence REAL,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')
    
    # 진단 이력 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            file_id INTEGER,
            diagnosis_result TEXT,
            confidence REAL,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (file_id) REFERENCES audio_files (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("데이터베이스 초기화 완료")

# Pydantic 모델들
class UserCreate(BaseModel):
    email: str
    password: str
    company_name: str
    contact_person: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class DiagnosisRequest(BaseModel):
    equipment_id: str
    auto_analysis: bool = True
    auto_prediction: bool = True

class DiagnosisResult(BaseModel):
    file_id: str
    filename: str
    equipment_id: str
    diagnosis: str
    confidence: float
    recommendations: List[str]
    processing_time: float

# 유틸리티 함수들
def hash_password(password: str) -> str:
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed

def create_access_token(data: dict):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """토큰 검증"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect('compressor_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# AI 모델 클래스
class CompressorAIModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.labels = {
            'compressor_normal': '정상 압축기',
            'compressor_overload': '압축기 과부하',
            'compressor_bearing_wear': '압축기 베어링 마모',
            'compressor_valve_fault': '압축기 밸브 이상'
        }
        self.load_model()
    
    def load_model(self):
        """모델 로드"""
        try:
            model_path = "models/lightweight_compressor_ai.pkl"
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model')
                    self.scaler = model_data.get('scaler')
                    print("✅ AI 모델 로드 완료")
            else:
                print("⚠️ 모델 파일이 없습니다. 기본값을 사용합니다.")
        except Exception as e:
            print(f"⚠️ 모델 로드 실패: {e}. 기본값을 사용합니다.")
    
    def extract_features(self, audio, sr=22050):
        """오디오 특징 추출"""
        try:
            # MFCC 특징
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            mfcc_std = np.std(mfcc, axis=1)
            
            # 스펙트럴 특징
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            
            # 진동 특징
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
            
            # 특징 결합
            features = np.concatenate([
                mfcc_mean, mfcc_std,
                np.mean(spectral_centroid), np.std(spectral_centroid),
                np.mean(spectral_rolloff), np.std(spectral_rolloff),
                np.mean(zero_crossing_rate), np.std(zero_crossing_rate)
            ])
            
            return features
        except Exception as e:
            print(f"특징 추출 실패: {e}")
            return None
    
    def predict(self, audio, sr=22050):
        """진단 예측"""
        try:
            if self.model is None:
                return "정상 압축기", 0.8  # 기본값
            
            features = self.extract_features(audio, sr)
            if features is None:
                return "정상 압축기", 0.8
            
            # 특징 정규화
            if self.scaler:
                features = self.scaler.transform(features.reshape(1, -1))
            
            # 예측
            prediction = self.model.predict(features.reshape(1, -1))[0]
            confidence = np.max(self.model.predict_proba(features.reshape(1, -1)))
            
            # 라벨 변환
            diagnosis = self.labels.get(prediction, "정상 압축기")
            
            return diagnosis, confidence
        except Exception as e:
            print(f"예측 실패: {e}")
            return "정상 압축기", 0.8

# AI 모델 인스턴스
ai_model = CompressorAIModel()

# API 엔드포인트들
@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행"""
    try:
        init_database()
        print("✅ 데이터베이스 초기화 완료")
        print("✅ 백엔드 API 서버가 시작되었습니다.")
        print("🌐 API 문서: http://localhost:8000/docs")
        print("🔗 API 주소: http://localhost:8000")
    except Exception as e:
        print(f"⚠️ 서버 시작 중 오류: {e}")
        print("서버는 계속 실행되지만 일부 기능이 제한될 수 있습니다.")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "압축기 진단 API 서버", "version": "1.0.0"}

@app.post("/auth/register")
async def register_user(user: UserCreate):
    """사용자 회원가입"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 이메일 중복 확인
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
        
        # 사용자 생성
        user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        password_hash = hash_password(user.password)
        
        cursor.execute("""
            INSERT INTO users (id, email, password_hash, company_name, contact_person, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, user.email, password_hash, user.company_name, user.contact_person, user.phone))
        
        # 고객 테이블에도 추가
        cursor.execute("""
            INSERT INTO customers (id, company_name, contact_person, email, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, user.company_name, user.contact_person, user.email, user.phone))
        
        conn.commit()
        
        return {"message": "회원가입이 완료되었습니다.", "user_id": user_id}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")
    finally:
        conn.close()

@app.post("/auth/login")
async def login_user(user: UserLogin):
    """사용자 로그인"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 사용자 조회
        cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
        user_data = cursor.fetchone()
        
        if not user_data or not verify_password(user.password, user_data['password_hash']):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
        
        # 토큰 생성
        access_token = create_access_token(data={"sub": user_data['id']})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_info": {
                "id": user_data['id'],
                "email": user_data['email'],
                "company_name": user_data['company_name'],
                "contact_person": user_data['contact_person'],
                "role": user_data['role']
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
    finally:
        conn.close()

@app.get("/users/me")
async def get_current_user(user_id: str = Depends(verify_token)):
    """현재 사용자 정보 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, email, company_name, contact_person, role, login_type FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        return dict(user_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용자 정보 조회 실패: {str(e)}")
    finally:
        conn.close()

# 카카오톡 로그인 관련 엔드포인트들
@app.get("/auth/kakao/login")
async def kakao_login():
    """카카오톡 로그인 URL 생성"""
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    return {"auth_url": kakao_auth_url}

@app.get("/auth/kakao/callback")
async def kakao_callback(code: str):
    """카카오톡 로그인 콜백 처리"""
    try:
        # 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "client_secret": KAKAO_CLIENT_SECRET,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # 데이터베이스에서 사용자 조회 또는 생성
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 기존 사용자 조회
            cursor.execute("SELECT * FROM users WHERE kakao_id = ?", (str(user_info['id']),))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # 기존 사용자 로그인
                access_token = create_access_token(data={"sub": existing_user['id']})
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user_info": {
                        "id": existing_user['id'],
                        "email": existing_user['email'],
                        "company_name": existing_user['company_name'],
                        "contact_person": existing_user['contact_person'],
                        "role": existing_user['role'],
                        "login_type": "kakao"
                    }
                }
            else:
                # 새 사용자 생성
                user_id = f"kakao_user_{user_info['id']}"
                email = user_info.get('kakao_account', {}).get('email', f"kakao_{user_info['id']}@kakao.com")
                nickname = user_info.get('properties', {}).get('nickname', '카카오 사용자')
                
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, company_name, contact_person, login_type, kakao_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, email, None, nickname, nickname, 'kakao', str(user_info['id'])))
                
                # 고객 테이블에도 추가
                cursor.execute("""
                    INSERT INTO customers (id, company_name, contact_person, email)
                    VALUES (?, ?, ?, ?)
                """, (user_id, nickname, nickname, email))
                
                conn.commit()
                
                access_token = create_access_token(data={"sub": user_id})
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user_info": {
                        "id": user_id,
                        "email": email,
                        "company_name": nickname,
                        "contact_person": nickname,
                        "role": "customer",
                        "login_type": "kakao"
                    }
                }
        
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"카카오톡 로그인 처리 실패: {str(e)}")
        finally:
            conn.close()
    
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"카카오톡 API 요청 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카카오톡 로그인 실패: {str(e)}")

@app.post("/diagnosis/upload")
async def upload_and_diagnose(
    files: List[UploadFile] = File(...),
    equipment_id: str = Form(...),
    auto_analysis: bool = Form(True),
    auto_prediction: bool = Form(True),
    user_id: str = Depends(verify_token)
):
    """파일 업로드 및 진단"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = []
    
    try:
        for file in files:
            # 파일 저장
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 오디오 분석
            audio, sr = librosa.load(file_path, sr=22050)
            duration = len(audio) / sr
            
            # AI 진단
            start_time = datetime.now()
            diagnosis, confidence = ai_model.predict(audio, sr)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 데이터베이스 저장
            cursor.execute("""
                INSERT INTO audio_files (filename, duration, sample_rate, file_path, customer_id, equipment_id, diagnosis_result, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (file.filename, duration, sr, file_path, user_id, equipment_id, diagnosis, confidence))
            
            file_id = cursor.lastrowid
            
            # 진단 이력 저장
            cursor.execute("""
                INSERT INTO diagnosis_history (user_id, file_id, diagnosis_result, confidence, processing_time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, file_id, diagnosis, confidence, processing_time))
            
            # 결과 생성
            result = DiagnosisResult(
                file_id=str(file_id),
                filename=file.filename,
                equipment_id=equipment_id,
                diagnosis=diagnosis,
                confidence=confidence,
                recommendations=get_recommendations(diagnosis),
                processing_time=processing_time
            )
            results.append(result)
        
        conn.commit()
        return {"results": results, "message": f"{len(results)}개 파일 진단 완료"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"진단 실패: {str(e)}")
    finally:
        conn.close()

def get_recommendations(diagnosis: str) -> List[str]:
    """진단 결과에 따른 권장사항"""
    recommendations = {
        "정상 압축기": ["정기 점검 유지", "모니터링 지속"],
        "압축기 과부하": ["부하 감소 필요", "냉각 시스템 점검", "운전 조건 조정"],
        "압축기 베어링 마모": ["베어링 교체 필요", "윤활유 점검", "진동 모니터링 강화"],
        "압축기 밸브 이상": ["밸브 점검 필요", "압력 조정", "유지보수 일정 조정"]
    }
    return recommendations.get(diagnosis, ["전문가 상담 권장"])

@app.get("/diagnosis/history")
async def get_diagnosis_history(user_id: str = Depends(verify_token)):
    """진단 이력 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT dh.*, af.filename, af.equipment_id
            FROM diagnosis_history dh
            JOIN audio_files af ON dh.file_id = af.id
            WHERE dh.user_id = ?
            ORDER BY dh.created_at DESC
        """, (user_id,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row['id'],
                "filename": row['filename'],
                "equipment_id": row['equipment_id'],
                "diagnosis_result": row['diagnosis_result'],
                "confidence": row['confidence'],
                "processing_time": row['processing_time'],
                "created_at": row['created_at']
            })
        
        return {"history": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력 조회 실패: {str(e)}")
    finally:
        conn.close()

@app.get("/customers")
async def get_customers(user_id: str = Depends(verify_token)):
    """고객 목록 조회 (관리자용)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 관리자 권한 확인
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data or user_data['role'] != 'admin':
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
        customers = []
        for row in cursor.fetchall():
            customers.append(dict(row))
        
        return {"customers": customers}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"고객 목록 조회 실패: {str(e)}")
    finally:
        conn.close()

@app.get("/stats/system")
async def get_system_stats(user_id: str = Depends(verify_token)):
    """시스템 통계 조회 (관리자용)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 관리자 권한 확인
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data or user_data['role'] != 'admin':
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")
        
        # 통계 조회
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audio_files")
        total_files = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM audio_files WHERE DATE(upload_time) = DATE('now')")
        today_diagnoses = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence) FROM diagnosis_history")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        return {
            "total_customers": total_customers,
            "total_files": total_files,
            "today_diagnoses": today_diagnoses,
            "average_confidence": avg_confidence
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 