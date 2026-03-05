# 시각적 유사도 모델 (Visual Similarity Model)

ResNet50 기반 Triplet Network를 이용한 이미지 유사도 측정 모델입니다.

## 📦 구성 요소

| 파일명                       | 설명                                     |
| ---------------------------- | ---------------------------------------- |
| `model_utils.py`             | 모델 로드, 임베딩 생성, 유사도 계산 함수 |
| `db_example.py`              | DB 연동 사용 예제                        |
| `resnet50_triplet_final.pth` | 학습된 모델 가중치 (PyTorch)             |

## 🚀 설치 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Python 버전

- **권장**: Python 3.8 이상
- **테스트**: Python 3.9, 3.10, 3.11

### 3. GPU 사용 (선택사항)

```bash
# CUDA 지원 PyTorch 설치 (권장)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 💡 사용 방법

### 기본 사용법

```python
from model_utils import load_trained_model, get_embedding, get_cosine_similarity
import torch

# 1. 디바이스 선택 (GPU 또는 CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 2. 모델 로드
model = load_trained_model('resnet50_triplet_final.pth', device)

# 3. 이미지를 128차원 벡터로 변환
embedding = get_embedding('image.jpg', model, device)
# embedding: numpy array, shape (128,)

# 4. 두 이미지의 유사도 계산
query_embedding = get_embedding('query.jpg', model, device)
db_embedding = get_embedding('db_image.jpg', model, device)
similarity = get_cosine_similarity(query_embedding, db_embedding)
# similarity: 0.0 ~ 1.0 (1에 가까울수록 유사)
```

## 🔧 모델 상세

### 구조

- **Backbone**: ResNet50 (ImageNet 사전학습)
- **임베딩 차원**: 128
- **정규화**: L2 정규화 (코사인 유사도용)
- **학습방식**: Triplet Loss

### 입력

- **이미지 크기**: 224×224 RGB
- **전처리**: ImageNet 표준화 (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

### 출력

- **임베딩**: 128차원 정규화된 벡터
- **유사도**: 0.0~1.0 범위 (코사인 유사도)

## 📊 유사도 판정 기준 (Threshold Guide)

본 모델의 특성을 고려한 현실적인 유사도 판정 기준입니다:

범위 (Score),판정 결과,상세 설명 및 대응 가이드
0.7 ~ 1.0,🟢 매우 높음,동일 개체: 해상도/밝기/각도만 약간 다른 동일 로고. (자동 매칭 가능)
0.3 ~ 0.7,🟡 보통 (유사),"스타일 변형: 컬러↔흑백 변환, 보조 텍스트 추가, 배경 노이즈 포함 등. (수동 검토 권장)"
0.2 ~ 0.3,🟠 경계 단계,형태적 유사: 브랜드는 다르나 실루엣이나 구도가 닮은 경우. (추천 후보군 노출)
0.2 미만,🔴 낮음,비유사: 특징점이 일치하지 않는 서로 다른 브랜드. |

### 💡 DB팀 전달 팁

**1. 색상 민감도 (Color Sensitivity)**

- **"모델이 RGB 색상 특징에 매우 예민합니다."**
- 동일 로고라도 컬러와 흑백 변환 시 유사도가 **0.3 ~ 0.4 수준**으로 낮게 측정될 수 있습니다.
- 판정 로직에 이를 반영하여 임계값을 너무 높게 설정하지 마세요.

**2. 권장 임계값 (Recommended Threshold)**

- 시스템에서 **'유사 로고'로 분류하여 노출할 최소 기준선은 0.25 ~ 0.3**을 권장합니다.
- 상위 10개 검색 결과 중 **0.25 이상의 항목들을 사용자에게 '유사한 로고 후보'로 제안**하는 것이 가장 정확도가 높습니다.

**3. 최적화 (Performance Optimization)**

- 임베딩은 **L2 정규화가 완료된 상태**이므로, 코사인 유사도 계산 시 복잡한 수식 대신 **단순 내적(numpy.dot)**을 사용하세요.
- 이는 벡터 DB 검색 속도를 크게 향상시킵니다.

# 판정 로직 예시 코드

THRESHOLD = 0.3

if similarity >= 0.7:
result = "동일 로고 (Match)"
elif similarity >= THRESHOLD:
result = "유사 로고 (Candidate)"
else:
result = "판정 제외 (Mismatch)"

## 📊 DB 연동 방법

### 1. 초기 인덱싱 (DB 벡터 저장)

- 각 이미지의 128차원 벡터를 추출하여 DB에 저장합니다.
- 벡터 데이터는 이미 **L2 정규화**가 완료된 상태입니다.

```sql
-- PostgreSQL (pgvector 사용 시) 예시
CREATE TABLE logo_embeddings (
    id SERIAL PRIMARY KEY,
    brand_name VARCHAR(100),
    image_path TEXT,
    embedding vector(128)  -- 128차원 벡터 타입
);
```

### 2. 검색 시 (유사 이미지 찾기)

```python
# N개 데이터에 대한 일괄 유사도 검색 예시
query_embedding = get_embedding('user_upload.jpg', model, device) # (128,)
db_embeddings = np.array([...]) # DB에서 불러온 (N, 128) 행렬

# 단순 내적만으로 유사도 계산 (속도가 매우 빠름)
similarities = np.dot(db_embeddings, query_embedding) # 결과: (N,) 벡터
top_k_indices = np.argsort(-similarities)[:10]
```

## ⚠️ 주의사항

1. **모델 파일 위치**: `resnet50_triplet_final.pth`가 지정된 경로에 있어야 함
2. **이미지 형식**: JPG, PNG, BMP 등 PIL이 읽을 수 있는 형식
3. **메모리**: GPU 메모리는 약 2GB, CPU는 약 4GB 필요 (배치 크기에 따라 변동)
4. **성능**:
   - GPU (CUDA): ~50ms/이미지
   - CPU: ~200ms/이미지
