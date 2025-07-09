# MIMII 축소 데이터셋

## 📊 패키지 구성
- **특징 데이터**: features/ - 머신러닝용 압축된 특징벡터
- **데모 오디오**: demo_audio/ - 테스트용 샘플 (10개)
- **총 크기**: 2.4MB (Git 친화적)

## 🚀 사용 방법

### 특징 데이터 로드
```python
import pandas as pd
features = pd.read_csv('features/compressed_features.csv')
print(f"특징 차원: {features.shape}")
```

### 데모 오디오 재생
```python
import librosa
audio, sr = librosa.load('demo_audio/demo_00_normal.wav')
print(f"오디오 길이: {len(audio)/sr:.1f}초")
```
