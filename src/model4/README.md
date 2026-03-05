# 상표 관념 유사도 분석 시스템

상표 이미지를 GPT를 통해 분석하고, 임베딩을 생성하여 유사도를 계산하는 시스템입니다.

## 구조

- **trademark_analysis.py**: Azure OpenAI를 사용하여 상표 이미지를 분석하고 임베딩 생성
- **compare.py**: 생성된 임베딩을 이용해 유사도 계산
- **config.py**: 환경 설정 관리
- **.env**: 환경 변수 설정 (`.env.example` 참고)

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

`.env.example`을 `.env`로 복사하고 본인의 Azure OpenAI 정보를 입력하세요:

```bash
cp .env.example .env
```

`.env` 파일 수정:

```
AZURE_API_KEY=your_api_key_here
AZURE_API_VERSION=2024-05-01-preview
AZURE_ENDPOINT=https://your-resource-name.openai.azure.com/
MODEL_NAME=gpt-5.1-chat
EMBEDDING_MODEL=text-embedding-3-large
TARGET_DIR=./test_images/target
CANDIDATE_DIR=./test_images/candidates
OUTPUT_FILE=data.jsonl
SLEEP_TIME=0.5
```

## 사용 방법

### 1. 상표 분석 및 임베딩 생성

```bash
python trademark_analysis.py
```

- `./test_images/target/`: 기준 상표 이미지 (TARGET이 파일명에 포함)
- `./test_images/candidates/`: 후보 상표 이미지들
- 결과: `data.jsonl` 파일 생성

### 2. 유사도 계산

```python
from compare import analyze_similarity

results = analyze_similarity("data.jsonl")
# results: {타겟_파일명: [(후보_파일명, 유사도), ...]}
```

## 주요 함수

### trademark_analysis.py

- `generate_description(image_path)`: 상표 이미지 분석 및 설명 생성
- `get_embedding(text)`: 텍스트를 벡터로 변환
- `run_test()`: 전체 분석 실행

### compare.py

- `calculate_similarity(target_embedding, candidate_embeddings)`: 유사도 계산
- `load_from_jsonl(file_path)`: JSONL 파일에서 데이터 로드
- `analyze_similarity(jsonl_file)`: 전체 유사도 분석 실행 및 결과 반환

## 출력 형식

### data.jsonl

```json
{
  "file_name": "TARGET_logo.jpg",
  "description": "상표의 관념 설명...",
  "embedding": [0.123, 0.456, ...]
}
```

### analyze_similarity() 반환값

```python
{
  "TARGET_logo.jpg": [
    ("candidate1.jpg", 0.95),
    ("candidate2.jpg", 0.87),
    ...
  ]
}
```

## DB 연동

현재는 로컬 파일 시스템 기반입니다. DB 연동이 필요한 경우, 다음을 수정하면 됩니다:

1. `run_test()` 함수 내 데이터 로드 부분 → DB 쿼리로 변경
2. JSONL 저장 부분 → DB INSERT/UPDATE로 변경
3. `analyze_similarity()` → DB에서 데이터 로드 후 처리

## 주의사항

- Azure OpenAI API 키는 절대 코드에 하드코딩하지 마세요. `.env` 파일로 관리하세요.
- Rate Limit 회피를 위해 API 호출 사이에 딜레이(`SLEEP_TIME`)를 설정했습니다.
- 대량의 이미지 처리 시 API 비용이 발생할 수 있습니다.

## 모델4 개발자의 유사도 체감 정도

- 관념적 모델은 0.6 이상이면 침해 가능성이 높다고 봐도 무방합니다 ~

- <관념적 유사도 측정값 기준>
- 0.3 미만 : 유사도 매우 낮음
- 0.4 ~ 0.49 : 유사도 낮음
- 0.50 ~ 0.59 : 의미적 유사 가능성 있음
- 0.60 ~0.69 : 침해 가능성 높음(검토필요)
- 0.70 ~이상 : 침해 가능성 매우 높음(검토필요X)
