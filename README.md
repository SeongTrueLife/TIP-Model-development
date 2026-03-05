# Trademark AI Models 🤖

본 레포지토리는 **상표 침해 모니터링 및 법리 기반 침해 여부 분석 프로젝트(TIP-Trademark_Project)** 의 핵심 **AI 모델 파이프라인 및 아키텍처** 코드만을 분리하여 모아둔 저장소입니다.

> 🚨 **안내 사항**
>
> 이 레포지토리는 모델 연구, 실험(EDA), 데이터 파이프라인 구축 과정을 담고 있는 서브 모듈 성격의 저장소입니다.
> 실제 서비스에 연동되는 **전체 프로젝트 MVP 완성본**은 아래 메인 레포지토리를 참고해 주시기 바랍니다.
>
> - 🔗 **Main Repository:** [TIP-Trademark_Project (https://github.com/SeongTrueLife/TIP-Trademark_Project)](#)

---

## 📂 프로젝트 구조 (Project Structure)

프로젝트는 발전 과정에 따라 여러 모델(Model 1 ~ Model 5)로 구성되어 있습니다. 각 모델은 시각, 호칭, 관념적 유사도 등 상표 분석의 특정 측면을 담당하며, 최종적으로 **Model 5**를 통해 통합된 앙상블 파이프라인(LangGraph 기반)으로 완성되었습니다.

### 1️⃣ Model 1: Visual Detection & Background Removal

- **기능:** 상표 이미지에서 불필요한 배경을 제거하고 핵심 상표 객체만 추출 (누끼 따기)
- **주요 기술:** YOLO v11 (객체 탐지) + SAM 2 (정밀 이미지 분할)
- **특이사항:** `sam2.1_b.pt` 모델은 용량 문제로 레포지토리에 포함되지 않았습니다. 코드를 처음 실행할 때 `ultralytics` 라이브러리를 통해 자동 다운로드됩니다.

### 2️⃣ Model 2 & 3: Vision & Phonetic Analysis (Core Models)

- **Model 2 (Visual):** ResNet 기반 Triplet Loss 학습을 통해 상표 이미지 간의 **시각적 외관 유사도** 추출
- **Model 3 (Phonetic):** Azure OpenAI LLM 기반의 프롬프트 엔지니어링을 활용하여 두 상표명 간의 **호칭(발음) 유사도** 비교 및 평가

### 3️⃣ Model 4: Semantic Analysis & Data Management

- **기능:** 텍스트 임베딩을 활용하여 상표가 가지는 의미적, **관념적 유사도**를 비교
- **주요 기술:** Azure OpenAI `text-embedding-3-large` 활용 벡터 비교

### 4️⃣ Model 5: Integrated Pipeline (LangGraph) - ✨ Final Architecture

- **기능:** 개별적으로 동작하던 Model 1~4를 하나의 AI 에이전트 파이프라인으로 통합. 시각/호칭/관념 유사도 점수를 종합 분석하여 최종 침해 리스크 스코어 산출
- **주요 기술:** `LangGraph` 기반 노드(Node) 오케스트레이션, LLM을 활용한 최종 사유 생성, RAG 기반 판례 검색 연동
- **흐름(Pipeline):**
  1. `Node 0`: 각 모델의 원시 점수(Raw Score) 정규화(Calibration)
  2. `Node 1~4`: 시각, 호칭, 관념, 검색 에이전트 병렬 실행
  3. `Node 5`: 동적 가중치 할당 매퍼(Dynamic Weight Mapper)
  4. `Node 6`: 최종 유사도 계산 및 리스크 등급(High/Medium/Low/Safe) 판정

---

## ⚙️ 실행 및 환경 설정 (Setup)

### 1. 보안 키 설정 (.env)

본 저장소에는 보안을 위해 `API Key`가 포함된 `.env` 파일이 업로드되지 않습니다.
각 모델 폴더(`model3`, `model4`, `model5` 등)에 위치한 `.env.example` 파일을 복사하여 `.env` 파일을 생성한 뒤, 본인의 환경에 맞는 Azure API 키와 DB 비밀번호를 입력해야 합니다.

### 2. 필수 라이브러리 설치

프로젝트 루트 또는 각 모델 폴더 안의 `requirements.txt`를 통해 의존성을 설치합니다.
(현재 통합 버전용은 제공되지 않으며, 각 개별 모델 폴더 내 `requirements.txt`를 참고해 주세요.)

```bash
# 예시: Model 3 실행 시
pip install -r src/model3/requirements.txt
```

### 3. 무거운 모델 파일 가이드

- `Model 1`의 YOLO 가중치(`best.pt`)는 레포지토리 내에 포함되어 있습니다 (`src/model1/yolo/best.pt`).
- SAM 2 모델 가중치는 스크립트(`pipeline.py` 등)를 최초 실행할 때 인터넷을 통해 로컬로 자동 다운로드됩니다.

---

## 📊 결과 분석 및 실험 (Reports)

- `src/report` 및 각 폴더 내 마크다운 문서를 통해 각 모델의 임계값(Threshold) 튜닝 과정, Baseline 비교, Precision/Recall 성능 개선 결과 등 모델 고도화 과정을 확인하실 수 있습니다.
