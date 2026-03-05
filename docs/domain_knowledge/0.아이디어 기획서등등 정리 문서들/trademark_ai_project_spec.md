# 상표권 침해 AI 분석 시스템 (TrademarkGuard)

## 프로젝트 최종 기획안

**작성일**: 2026년 1월 9일  
**팀**: MS AI School 프로젝트 팀  
**상태**: MVP 개발 단계

---

## 목차

1. [Executive Summary](#executive-summary)
2. [시장 분석](#시장-분석)
3. [제품 정의](#제품-정의)
4. [기술 아키텍처](#기술-아키텍처)
5. [법리 기반 설계](#법리-기반-설계)
6. [구현 계획](#구현-계획)
7. [예상 성과](#예상-성과)
8. [리스크 관리](#리스크-관리)
9. [팀 및 협력 전략](#팀-및-협력-전략)

---

## Executive Summary

### 프로젝트 개요

**TrademarkGuard**는 상표권 침해 하는 상표들을 수집하고 침해판정을 위한 AI 분석 시스템으로, 변리사와 기업의 상표 모니터링 업무를 3배 효율화합니다.

### 핵심 가치 제안 (Value Proposition)

| 관점          | 기존 방식 (MarqVision 등) | TrademarkGuard                  |
| ------------- | ------------------------- | ------------------------------- | --------------- |
| **대상**      | B2C 브랜드                | **B2B (변리사, 법무법인)**      | B2G(지식재산처) |
| **문제**      | 위조품 탐지만 가능        | **상표 유사도 판정까지 가능**   |
| **범위**      | 상품 쇼핑몰               | **상품 + 서비스업 (지도, SNS)** |
| **권리행사**  | 자동 삭제 (플랫폼)        | **법적 근거 제공 (소송 지원)**  |
| **처리 시간** | 2-3일                     | 3개월-2년 (법적 절차)           |
| **비용**      | 낮음                      | 변리사 의존도 ↓ (구독형)        |

### 시장 기회

- 한국 상표 침해 분쟁 연간 3,000건 이상
- 변리사 수급 부족 (시간당 비용 ₩50-100만)
- 디지털화 미흡 (대부분 수작업)
- **미개척 시장: 상표 유사도 분석 AI 서비스 부재**

### 경쟁 우위

1. **법리 기반 설계**: 상표법 3요소(외관/호칭/관념) + 요부관찰 반영
2. **도메인 전문성**: 변리사 네트워크 활용 (베타 테스트, 데이터 검증)
3. **설명 가능성**: Black-box 아님, 각 요소별 점수 투명 공개
4. **확장성**: MVP부터 엔터프라이즈까지 수평적 확장 가능

---

## 시장 분석

### 시장 규모

#### 대상 시장 (TAM: Total Addressable Market)

```
상표 등록 기업: 약 50만 개
× 연간 침해 모니터링 필요도: 상위 20% (10만 개)
× 평균 구독료: ₩80만/월
= TAM: 약 ₩960억/연
```

#### 현실적 시장 (SAM: Serviceable Addressable Market)

```
변리사, 로펌, 기업 법무팀: 약 3,000개 (고객 기준)
× 평균 구독료: ₩80만/월
= SAM: 약 ₩288억/연
```

#### 달성 가능 시장 (SOM: Serviceable Obtainable Market, Year 1-2)

```
목표 고객: 50-100개
× 평균 구독료: ₩80만/월
= SOM: 약 ₩48-96억/연
```

### 경쟁 분석

#### 직접 경쟁: MarqVision, Red Points 등

- **강점**: 위조품 탐지 빠름, 자동 삭제, 높은 성공률(98%)
- **약점**: 위조품만 대응, 법적 근거 없음, 상업화된 서비스
- **우리의 차별점**: **유사 상표(위조 아님)까지 법적 분석 제공**

#### 간접 경쟁: 변리사 수작업

- **강점**: 정확도, 법적 신뢰성
- **약점**: 느림(3개월-2년), 비쌈(₩500만-₩2,000만), 공급 부족
- **우리의 차별점**: **변리사의 1차 필터링 자동화 (시간 3배 단축)**

#### 경쟁 우위 매트릭스

```
                정확도
                  ↑
                  |
        변리사 ✓ |
                  | ◇ 우리 (고도화 후)
                  |
        우리 ◇   |
    (MVP) MarqVision ✓
                  |
              ——————→ 속도
```

---

## 제품 정의

### 핵심 기능

#### Feature 1: 자동 모니터링 (Automatic Monitoring)

```
• 오픈마켓 (쿠팡, 네이버 쇼핑, 마켓컬리 등)
• 네이버 지도, 카카오맵 (서비스업)
• SNS (인스타그램, 페이스북)

→ 매일 크롤링 + AI 분석 + 의심 건 추출
```

#### Feature 2: 3요소 분석 (Three-Factor Analysis)

```
Model 2: 외관 유사도 (Visual Similarity)
  - 도형, 색상, 구성 분석
  - ViT (Vision Transformer)
  - 점수: 0-100

Model 3: 호칭 유사도 (Phonetic Similarity)
  - 발음 유사도 (한글 자모 분해)
  - Levenshtein Distance
  - 점수: 0-100

Model 4: 관념 유사도 (Conceptual Similarity)
  - 의미 유사도
  - KoBERT (한글 임베딩)
  - 점수: 0-100
```

#### Feature 3: 요부관찰 반영 (Essential Features Weighting)

```
Model 5: 동적 가중치 모델

입력: 상표 특성 (텍스트/도형/혼합)
      + 지정상품 (니스 분류)
      + 3요소 점수

출력: 최종 침해 점수 (0-100)
     + 가중치 분석 (어느 요소가 중요했는가)

예시:
- 텍스트 상표 "NIKE"
  → 호칭 60%, 외관 20%, 관념 20%
  → 호칭 유사도에 가중

- 도형 상표 (Nike Swoosh)
  → 외관 70%, 호칭 15%, 관념 15%
  → 외관 유사도에 가중
```

#### Feature 4: 위험도 분류 (Risk Classification)

```
고위험 (80점 이상)
→ 침해 가능성 높음
→ 즉시 경고장 발송 권장

중위험 (60-79점)
→ 침해 가능성 중간
→ 변리사 검토 후 판단

저위험 (59점 이하)
→ 침해 가능성 낮음
→ 계속 모니터링
```

#### Feature 5: 법리 근거 보고서 (Legal Report)

```
• 침해 점수 + 근거
• 판례 인용 (유사한 선례 3-5건)
• 법적 의견 (AI + LLM 자동 생성)
• 권리행사 옵션 (경고장/소송 등)

→ 변리사가 바로 의뢰인에게 설명 가능
```

### 사용자 시나리오

#### Scenario 1: 변리사 (개인)

```
월요일 아침:
1. 대시보드 접속
2. 지난주 수집된 의심 건 10개 확인
3. 고위험 2건 선택
4. AI 분석 + 판례 근거 확인
5. 경고장 템플릿 자동 생성
6. 의뢰인에게 보고

소요 시간: 30분 (기존 3시간 → 3배 단축)
```

#### Scenario 2: 로펌 (팀 단위)

```
매주 목요일 회의:
1. 담당 변리사 5명
2. TrademarkGuard 리포트 공유
3. 고위험/중위험 건 분담
4. 조치 결정

효과:
- 우선순위 자동 판단
- 팀 리소스 최적화
- 회의 시간 단축
```

#### Scenario 3: 기업 법무팀

```
월간 보고:
1. 자사 상표 침해 현황
2. 카테고리별 집계
3. 월간 추이 분석
4. 권리행사 결정

효과:
- 브랜드 보호 강화
- 법적 리스크 감소
- 경영 의사결정 지원
```

---

## 기술 아키텍처

### 전체 시스템 플로우

```
┌─────────────────────────────────────────────────────┐
│ 데이터 수집층 (Data Collection Layer)                │
├─────────────────────────────────────────────────────┤
│ • 오픈마켓 크롤링 (쿠팡, 네이버 쇼핑)               │
│ • 네이버 지도 크롤링 (비즈니스 정보)                 │
│ • SNS 크롤링 (인스타그램, 페이스북)                  │
│ • 대법원 판례 검색 (학습 데이터)                     │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 전처리층 (Preprocessing Layer)                       │
├─────────────────────────────────────────────────────┤
│ • 메타데이터 파싱 (브랜드명, 카테고리, 가격 등)      │
│ • 이미지/텍스트 정규화                               │
│ • 중복 제거                                          │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 1차 필터링 (First Filtering)                         │
├─────────────────────────────────────────────────────┤
│ • 니스 분류 기반 필터링                              │
│ • 정확히 동일한 상표 제거 (자체 등록자)              │
│ • 70% 탈락 → 비용 절감                               │
└────────────────┬────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────┐
│ 특성 추출층 (Feature Extraction Layer)               │
├─────────────────────────────────────────────────────┤
│ Model 1: 객체 탐지 (YOLO v8)                        │
│  → 이미지에서 상표 영역 추출                         │
└────────────────┬────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────┐
│ 분석층 (Analysis Layer) - 3요소 병렬 처리            │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Model 2: 외관 유사도              Model 3: 호칭 유사도
│ (Vision Transformer)              (한글 자모 분해)
│ • 도형 비교                        • 발음 비교
│ • 색상 비교                        • 자모 Levenshtein
│ • 구성 비교                        • 점수 0-100
│ • 점수 0-100
│                                    Model 4: 관념 유사도
│                                    (KoBERT)
│                                    • 의미 임베딩
│                                    • 코사인 유사도
│                                    • 점수 0-100
│                                                      │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│ 메타 학습층 (Meta-Learning Layer)                    │
├──────────────────────────────────────────────────────┤
│ Model 5: 동적 가중치 조율 (Rule-based → ML 진화)    │
│                                                      │
│ 입력: [외관점수, 호칭점수, 관념점수, 상표특성]      │
│ 처리: 상표 특성에 따라 가중치 결정                   │
│ 출력: [최종 점수, 가중치 분석, 근거]                │
│                                                      │
│ Rule-based 버전:                                     │
│ IF 텍스트상표: [0.2, 0.6, 0.2] (호칭 중시)         │
│ IF 도형상표: [0.7, 0.15, 0.15] (외관 중시)         │
│ ELSE: [0.4, 0.4, 0.2] (균형)                        │
│                                                      │
│ ML 버전 (고도화):                                    │
│ XGBoost로 판례 패턴 학습 → 가중치 자동 조율        │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│ 분류층 (Classification Layer)                        │
├──────────────────────────────────────────────────────┤
│ • 고위험 (80점 이상) → 즉시 조치                    │
│ • 중위험 (60-79점) → 검토 필요                      │
│ • 저위험 (59점 이하) → 계속 모니터링               │
└──────────────────┬───────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────┐
│ 보고층 (Reporting Layer)                             │
├──────────────────────────────────────────────────────┤
│ • 점수 + 위험도 표시                                 │
│ • 상세 분석 (3요소 각각의 점수)                      │
│ • 판례 근거 (유사 판례 3-5건 자동 인용)             │
│ • 권리행사 옵션 (경고장/소송 등)                     │
│ • LLM 기반 자동 보고서 생성                         │
└──────────────────────────────────────────────────────┘
```

### 기술 스택

#### 백엔드

- **언어**: Python 3.10+
- **프레임워크**: FastAPI (고성능 REST API)
- **데이터베이스**: PostgreSQL (메인) + MongoDB (로그/이력)
- **캐싱**: Redis (결과 캐싱)
- **잡 스케줄러**: Celery + Redis (크롤링 자동화)

#### ML/AI

- **객체 탐지**: YOLOv8 (Ultralytics)
- **이미지 처리**: PyTorch + Torchvision
- **NLP**: HuggingFace Transformers (KoBERT, BERT)
- **유사도 계산**: Scikit-learn (코사인 유사도, 거리 함수)
- **메타 모델**: 초기 규칙 기반 → XGBoost (고도화)

#### 프론트엔드

- **웹**: React.js (TypeScript)
- **UI 프레임워크**: Material-UI 또는 Ant Design
- **실시간**: WebSocket (결과 스트리밍)
- **차트**: Plotly / D3.js

#### 인프라

- **클라우드**: AWS / Google Cloud Platform (선택 후 결정)
- **컨테이너**: Docker + Kubernetes
- **모니터링**: Prometheus + Grafana
- **로깅**: ELK Stack (Elasticsearch + Logstash + Kibana)

### 데이터 플로우

```python
# MVP 코드 구조

from fastapi import FastAPI
from typing import Dict, List
import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import numpy as np

app = FastAPI()

class TrademarkAnalyzer:
    def __init__(self):
        # Model 2: 외관 유사도
        self.visual_model = VisualSimilarityModel()

        # Model 3: 호칭 유사도
        self.phonetic_model = PhoneticMatcher()

        # Model 4: 관념 유사도
        self.conceptual_model = ConceptualSimilarityModel()

        # Model 5: 메타 학습
        self.meta_learner = RuleBasedMetaLearner()

    def analyze(self,
                base_mark: Dict,
                target_mark: Dict) -> Dict:
        """
        기준 상표 vs 의심 상표 비교

        입력:
        {
            "image_url": "...",
            "text": "나이키",
            "type": "mixed",  # text/logo/mixed
            "nics": ["25"]    # 니스 분류
        }
        """

        # Step 1: 3요소 분석 (병렬 처리 가능)
        visual_score = self.visual_model.calculate(
            base_mark["image_url"],
            target_mark["image_url"]
        )

        phonetic_score = self.phonetic_model.calculate(
            base_mark["text"],
            target_mark["text"]
        )

        conceptual_score = self.conceptual_model.calculate(
            base_mark["text"],
            target_mark["text"]
        )

        # Step 2: 메타 모델
        final_score = self.meta_learner.combine(
            visual_score,
            phonetic_score,
            conceptual_score,
            base_mark["type"]
        )

        # Step 3: 위험도 분류
        risk_level = self.meta_learner.classify(final_score)

        # Step 4: 판례 검색 (RAG)
        similar_cases = self.retrieve_similar_cases(
            visual_score,
            phonetic_score,
            conceptual_score
        )

        return {
            "final_score": final_score,
            "risk_level": risk_level,
            "breakdown": {
                "visual": visual_score,
                "phonetic": phonetic_score,
                "conceptual": conceptual_score
            },
            "weights": self.meta_learner.get_weights(base_mark["type"]),
            "similar_cases": similar_cases,
            "recommendation": self.generate_recommendation(
                final_score,
                similar_cases
            )
        }

@app.post("/analyze")
def analyze_trademark(request: AnalysisRequest) -> Dict:
    analyzer = TrademarkAnalyzer()
    result = analyzer.analyze(
        request.base_mark,
        request.target_mark
    )
    return result
```

---

## 법리 기반 설계

### 상표법 기초

#### 상표권 침해 판정 기준 (상표법 제108조)

```
상표권 침해 성립 조건:

1. 상표의 동일·유사성 (필수)
   → Model 2, 3, 4 담당

2. 지정상품·서비스의 동일·유사성 (필수)
   → 1차 필터링 (니스 분류) 담당

3. 혼동 가능성 (필수)
   → Model 5 (메타 모델) 담당

4. 정당권원 없음 (필수)
   → 변리사 최종 검토 담당
```

### 상표 3요소 분석

#### 요소 1: 외관 유사도 (Visual Similarity)

```
정의: 상표를 보았을 때 시각적으로 혼동할 수 있는가?

판례 기준:
- 도형의 형태, 색상, 구성 비교
- 색상 차이는 비본질적 (회색 vs 검정 = 유사)
- 회전/크기 차이는 비본질적

AI 구현:
Model: Vision Transformer (ViT-B/32)
  • 224×224 이미지 입력
  • 1024차원 벡터 추출
  • 코사인 유사도 계산 (0-100)

학습 데이터:
  • ImageNet 사전학습 (일반 이미지)
  • Fine-tuning: 상표 이미지 100-500개

정확도 기대치:
  • MVP: 75-80%
  • 고도화: 85-90%
```

#### 요소 2: 호칭 유사도 (Phonetic Similarity)

````
정의: 발음했을 때 혼동할 수 있는가?

판례 기준 (한국):
- 호칭이 중요 ("TINTIN" = "틴틴" = 호칭 동일)
- 음절 수, 음운 유사도 비교
- 강조음, 길이 고려

예시:
- "나이키" vs "니이키" → 유사 (호칭 비교)
- "NIKE" vs "NIQUE" → 약간 유사

AI 구현:
방법: 한글 자모 분해 (규칙 기반)
  • "삼성" → ['ㅅ', 'ㅏ', 'ㅁ', 'ㅅ', 'ㅓ', 'ㅇ']
  • "쌤성" → ['ㅆ', 'ㅐ', 'ㅁ', 'ㅅ', 'ㅓ', 'ㅇ']
  • Levenshtein Distance: 2/6 = 66.7%

정확도:
  • MVP: 90-95% (규칙 기반이므로 높음)
  • 고도화: 95%+ (음소 기반 개선)

코드 예시:
```python
from jamo import h2j

def phonetic_similarity(mark1, mark2):
    jamo1 = h2j(mark1)
    jamo2 = h2j(mark2)
    distance = levenshtein(jamo1, jamo2)
    return (1 - distance / max(len(jamo1), len(jamo2))) * 100
````

#### 요소 3: 관념 유사도 (Conceptual Similarity)

```
정의: 의미가 같거나 유사한가?

판례 기준:
- 상표가 나타내는 의미 비교
- 조어(의미 없는 합성어)는 관념 무시
- 외래어는 해석이 필요

예시:
- "애플" vs "사과" → 의미 유사 (동일 개념)
- "나이키" vs "아디다스" → 의미 무관 (조어)
- "삼성" vs "삼급" → 약간 유사?

AI 구현:
모델: KoBERT (한글 특화 BERT)
  • 임베딩 768차원
  • 코사인 유사도 계산 (0-100)
  • 무의미 조어 필터링 추가

학습:
  • 사전학습: 한국어 위키피디아, 뉴스
  • Fine-tuning: 상표 관념 데이터 (100+ 예시)

정확도 기대치:
  • MVP: 60-65% (어려운 부분)
  • 고도화: 75-80% (LLM 활용)

한계:
  • 무의미 조어 판단 어려움
  • 문맥 의존적 의미 이해 부족
  • → 변리사 최종 검토 필수
```

### 요부관찰 (Essential Features Weighting)

````
정의: 상표의 핵심 식별 부분에 가중

판례 사례:
1. "SAMSUNG Galaxy"
   → 요부: "SAMSUNG" (유명 상표)
   → Galaxy: 보통명사 (비본질)
   → 호칭/외관 중시

2. Nike Swoosh (도형)
   → 요부: 체크 모양 (독특한 형태)
   → 외관 중시

3. "스타벅스"
   → 요부: "스타벅스" 전체 (유명 상표)
   → 발음 유사성 매우 중요

AI 구현:

MVP (규칙 기반):
```python
def get_weights(trademark_type):
    if trademark_type == "text":
        # 텍스트: 호칭 중시
        return {"visual": 0.2, "phonetic": 0.6, "conceptual": 0.2}
    elif trademark_type == "logo":
        # 로고: 외관 중시
        return {"visual": 0.7, "phonetic": 0.15, "conceptual": 0.15}
    else:  # mixed
        # 혼합: 균형
        return {"visual": 0.4, "phonetic": 0.4, "conceptual": 0.2}
````

고도화 (ML 기반):
• 판례 200건 학습
• XGBoost로 특성별 중요도 학습
• Attention Mechanism (Transformer)로 자동 가중치 계산

```

### 지정상품 필터링 (NICE Classification)

```

상표법 원칙:
"같은 상표라도 지정상품이 다르면 침해 아님"

예시:

- "Apple" (전자제품) vs "Apple 의원" (의료)
  → 업종 다름 → 혼동 가능성 낮음
- "Samsung" (전자) vs "Samsung 카페" (음식)
  → 업종 다름 → 단, 유명 상표면 보호 확대

구현:

1. NICE 분류 (1-45류)
2. 유사 여부 판단 (규칙 기반)
3. 비침해 건 70% 자동 필터링

예시 코드:

```python
NICE_SIMILARITY = {
    ("25", "25"): True,  # 의류 × 의류 = 유사
    ("25", "35"): False, # 의류 × 광고 = 비유사
    ("9", "42"): False,  # 전자 × IT서비스 = 비유사
    # 유명 상표는 예외 처리
}

def filter_by_nics(base_nics, target_nics):
    for b_nic in base_nics:
        for t_nic in target_nics:
            if NICE_SIMILARITY.get((b_nic, t_nic), False):
                return True  # 지정상품 유사
    return False  # 지정상품 비유사 → 스킵
```

```

### 판례 기반 검증

```

학습 데이터 로드맵:

Phase 1 (MVP, Week 5-6):
• 판례 30-50건 수집
• 변리사 레이블링
• 간단한 검증 (정확도 70%)

Phase 2 (베타, Month 2):
• 판례 100-150건 추가
• 패턴 분석
• 규칙 세분화

Phase 3 (고도화, Month 3-6):
• 판례 200-300건
• ML 모델 학습
• 정확도 85-90% 목표

판례 레이블링 템플릿:

```

| 판례 | 침해 | 외관 | 호칭 | 관념 | 핵심 요소 | 비고 |
|------|------|------|------|------|----------|------|
| 2023허1234 | O | 6 | 9 | 3 | 호칭 유사 | 텍스트상표 |
| 2023허5678 | X | 4 | 5 | 2 | 없음 | 업종 다름 |
| 2023허9012 | O | 8 | 7 | 5 | 외관+호칭 | 도형상표 |

```

---

## 구현 계획

### Phase 1: 기초 구축 (Week 1-2)

#### Task 1.1: 개발 환경 설정

```
[ ] Python 3.10+ 설정
[ ] Git 저장소 생성 (GitHub)
[ ] 가상환경 (venv)
[ ] 필수 라이브러리 설치
    - torch, torchvision
    - transformers
    - fastapi, uvicorn
    - selenium (크롤링)
    - jamo (한글)
[ ] AWS/GCP 계정 (선택)
```

#### Task 1.2: 데이터 수집 기반

```
[ ] 오픈마켓 크롤링 (Selenium)
    - 쿠팡 1,000개 상품
    - 네이버 쇼핑 500개
    - 저장: S3 또는 Local

[ ] 서비스업 크롤링 (Naver API)
    - 네이버 지도 500개 비즈니스
    - 저장: DB

[ ] 판례 수집 (대법원 홈페이지)
    - 상표 침해 판례 50-100건
    - 저장: JSON 포맷
```

### Phase 2: 개별 모델 구현 (Week 3-4)

#### Task 2.1: Model 3 (호칭 유사도) - 최우선

```python
# 소요 시간: 2-3일
# 복잡도: 낮음 (규칙 기반)

from jamo import h2j
from difflib import SequenceMatcher

class PhoneticMatcher:
    def decompose(self, text):
        return h2j(text)

    def levenshtein_distance(self, s1, s2):
        # 자모 간 편집 거리 계산
        pass

    def calculate_similarity(self, mark1, mark2):
        jamo1 = self.decompose(mark1)
        jamo2 = self.decompose(mark2)

        distance = self.levenshtein_distance(jamo1, jamo2)
        similarity = 1 - (distance / max(len(jamo1), len(jamo2)))

        return similarity * 100

# 테스트
matcher = PhoneticMatcher()
print(matcher.calculate_similarity("나이키", "니이키"))  # ~85
```

#### Task 2.2: Model 2 (외관 유사도)

```python
# 소요 시간: 1주
# 복잡도: 중간 (Transfer Learning)

import torch
import torchvision.models as models
from torchvision import transforms
from PIL import Image

class VisualSimilarityModel:
    def __init__(self):
        self.vit = models.vit_b_32(pretrained=True)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def extract_features(self, image_path):
        image = Image.open(image_path)
        tensor = self.transform(image).unsqueeze(0)

        with torch.no_grad():
            features = self.vit(tensor)

        return features

    def calculate_similarity(self, image1_path, image2_path):
        feat1 = self.extract_features(image1_path)
        feat2 = self.extract_features(image2_path)

        cosine_sim = torch.nn.functional.cosine_similarity(feat1, feat2)
        return (cosine_sim.item() + 1) / 2 * 100
```

#### Task 2.3: Model 4 (관념 유사도)

```python
# 소요 시간: 1주
# 복잡도: 높음 (BERT)

from transformers import AutoTokenizer, AutoModel
import torch

class ConceptualSimilarityModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            'skt/kobert-base-v1'
        )
        self.model = AutoModel.from_pretrained(
            'skt/kobert-base-v1'
        )

    def get_embedding(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :]

        return embedding

    def calculate_similarity(self, text1, text2):
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        cosine_sim = torch.nn.functional.cosine_similarity(emb1, emb2)
        return (cosine_sim.item() + 1) / 2 * 100
```

### Phase 3: 통합 및 테스트 (Week 5-6)

#### Task 3.1: 메타 모델 + 통합

```python
class TrademarkInfringementDetector:
    def __init__(self):
        self.visual = VisualSimilarityModel()
        self.phonetic = PhoneticMatcher()
        self.conceptual = ConceptualSimilarityModel()
        self.meta_learner = RuleBasedMetaLearner()

    def detect(self, base_mark, target_mark):
        # 3요소 분석
        visual = self.visual.calculate_similarity(...)
        phonetic = self.phonetic.calculate_similarity(...)
        conceptual = self.conceptual.calculate_similarity(...)

        # 메타 모델
        final_score = self.meta_learner.combine(
            visual, phonetic, conceptual,
            base_mark['type']
        )

        # 위험도 분류
        risk_level = self.meta_learner.classify(final_score)

        return {
            "score": final_score,
            "risk_level": risk_level,
            "breakdown": {
                "visual": visual,
                "phonetic": phonetic,
                "conceptual": conceptual
            }
        }
```

#### Task 3.2: 검증 (30개 판례)

```
테스트 케이스:
1. 명확한 침해 (호칭 유사)
   - 기대: High Risk
   - 실제 판결: 침해 O

2. 비침해 (업종 다름)
   - 기대: Low Risk
   - 실제 판결: 침해 X

3. 애매한 케이스 (중위험)
   - 기대: Medium Risk
   - 실제 판결: 케이스 바이 케이스

목표 정확도: 70%
```

### Phase 4: MVP 완성 (Week 7-8 선택)

#### 선택사항 (부트캠프 시간 제약 시 생략)

```
[ ] FastAPI 웹 서버 (간단)
[ ] CLI 인터페이스
[ ] 결과 JSON 출력
[ ] 깃허브 공개 (README 포함)
```

### 타임라인 (상세)

```
Week 1: 준비
  [Mon] 팀 회의 + 아이디어 브레인스토밍
  [Tue-Wed] 개발 환경 설정 + 저장소 생성
  [Thu-Fri] 데이터 수집 자동화 스크립트

Week 2: 데이터 수집
  [Mon-Fri] 병렬 크롤링 + 전처리
           (온라인 진행 가능)

Week 3: Model 3 (호칭 유사도)
  [Mon-Tue] 한글 자모 분해 + Levenshtein 구현
  [Wed] 테스트 + 최적화
  [Thu-Fri] 버그 수정 + 문서화

Week 4: Model 2 + Model 4
  [Mon-Tue] ViT 모델 다운로드 + 전처리
  [Wed] KoBERT 환경 설정
  [Thu] Model 2 구현 + 테스트
  [Fri] Model 4 구현 + 테스트

Week 5: Model 5 + 통합
  [Mon] 규칙 기반 메타 모델 구현
  [Tue-Wed] End-to-end 파이프라인
  [Thu-Fri] 통합 테스트

Week 6: 검증
  [Mon-Tue] 30개 판례로 검증
  [Wed] 정확도 분석 + 규칙 조정
  [Thu-Fri] 최종 버그 수정 + 발표 준비
```

---

## 예상 성과

### 기술 성과

#### 정확도 (Accuracy)

| 메트릭             | MVP (Week 6) | 베타 (Month 2) | 고도화 (Month 3) |
| ------------------ | ------------ | -------------- | ---------------- |
| **F1-score**       | 0.65-0.70    | 0.75-0.80      | 0.82-0.87        |
| **Precision**      | 70%          | 80%            | 85%              |
| **Recall**         | 65%          | 75%            | 80%              |
| **False Positive** | 25-30%       | 10-15%         | 5%               |

**해석**:

- MVP: 침해 10건 중 7건 탐지, 30% 오탐
- 베타: 침해 10건 중 8건 탐지, 10-15% 오탐
- 고도화: 침해 10건 중 8-9건 탐지, 5% 오탐 미만

#### 성능 (Performance)

```
처리 속도:
- 1건 분석: 3-5초 (GPU 기준)
- 100건 배치: 2-3분
- 크롤링 → 분석 → 보고: 1시간 (자동)

확장성:
- 동시 사용자: 100명 (초기)
- 월간 분석 건수: 10,000건 (MVP)
- 확장 후: 100,000건+
```

### 비즈니스 성과 (6개월)

#### 고객 확보

```
Timeline:
Month 1: 인터뷰 (3-5명 변리사)
Month 2: 베타 (5-10명 사용자)
Month 3: 정식 출시
  → 초기 고객 5-7명
Month 4-6: 네트워크 확장
  → 누적 15-20명

고객 구성:
- 개인 변리사: 60% (₩30만/월)
- 중소 로펌: 30% (₩80만/월)
- 기타: 10%

MRR (Monthly Recurring Revenue):
Month 3: ₩200-300만
Month 6: ₩940만
```

#### 재무 전망

```
Year 1 (2026):
- MRR (평균): ₩500만
- ARR: ₩6억
- 고객 수: 20-30명
- 매출 원가: 20% (클라우드 비용)
- 순이익률: 70% (초기)

Year 2 (2027):
- MRR: ₩2,000만
- ARR: ₩24억
- 고객 수: 80-100명
- 추가 투자 (마케팅): ₩5억

Year 3 (2028):
- MRR: ₩5,000만+
- ARR: ₩60억+
- 고객 수: 200명+
- 시리즈 A 투자 검토
```

### 사회 임팩트

```
변리사 업무 효율화:
- 상표 침해 모니터링 시간: 3배 단축
- 월간 추가 처리 건수: 50-100건
- 변리사 비용: 고객당 20-30% 감소

브랜드 보호 강화:
- 중소기업 상표 보호 접근성 향상
- 침해 탐지 시간: 3개월 → 1일
- 침해 제거 비율: 60% → 85%

법률 기술 발전:
- 한국 최초 상표 침해 AI 분석 서비스
- 판례 기반 AI 모델 공개 (가능 시)
- 변리사 교육 자료 제공
```

---

## 리스크 관리

### 기술적 리스크

#### Risk 1: 데이터 부족

```
문제: 상표 침해 판례 데이터 부족
영향도: 높음 (정확도 제약)
발생 확률: 높음

완화 방안:
1. 변리사 협력으로 판례 직접 수집
2. 전이학습 (Transfer Learning) 활용
3. 소수 데이터 학습 (Few-shot Learning)

실행:
- Week 3: 변리사 50개 판례 확보
- Week 5: 100개로 확대
- Month 2: 200개 목표
```

#### Risk 2: 모델 정확도 부족

```
문제: F1-score 60% 미만 (불합격)
영향도: 높음 (제품 실패)
발생 확률: 중간

완화 방안:
1. MVP 목표 재설정 (70%도 허용)
2. 변리사 피드백 루프
3. 규칙 기반 → ML 진화

실행:
- MVP: 규칙 기반으로 시작 (70% 목표)
- Month 2: XGBoost 추가 (75-80%)
- Month 3: 딥러닝 고도화 (85%+)
```

#### Risk 3: OCR 오류 (텍스트 인식)

```
문제: 이미지에서 텍스트 인식 실패
영향도: 중간 (호칭 분석 불가)
발생 확률: 중간

완화 방안:
1. Google Vision API (고정확도)
2. 여러 OCR 모델 앙상블
3. 수동 입력 옵션 제공

실행:
- MVP: Google Vision API 사용
- Month 2: Tesseract + Cloud Vision 앙상블
```

### 비즈니스 리스크

#### Risk 4: 고객 획득 어려움

```
문제: 변리사 채택 저조
영향도: 높음 (수익 부재)
발생 확률: 낮음 (네트워크 있음)

완화 방안:
1. 변리사 지인 10명 이상 확보
2. 무료 베타 기간 (3개월)
3. 50% 얼리 어댑터 할인

실행:
- Month 2: 베타 테스터 5-10명
- Month 3: 정식 고객 1명 이상 확보
- Month 6: 10명+ 목표
```

#### Risk 5: 법적 책임 문제

```
문제: AI 판단이 틀린 경우, 법적 책임?
영향도: 높음 (리스크)
발생 확률: 중간

완화 방안:
1. 명확한 약관: "참고 정보일 뿐, 변리사 검토 필수"
2. Uncertainty Estimation: "확신도" 표시
3. 책임 보험 검토

실행:
- MVP 출시 전: 약관 작성 (변호사 검토)
- 고객 가이드: "AI는 1차 필터일 뿐"
```

### 운영 리스크

#### Risk 6: 팀 구성원 이탈

```
문제: 부트캠프 종료 후 팀원 흩어짐
영향도: 높음
발생 확률: 중간

완화 방안:
1. 명확한 역할 분담
2. 마일스톤 기반 진행
3. 조기 단계부터 외부 자문가 확보

실행:
- Week 1: 팀 계약서 작성 (구속력 X)
- Month 1: 변리사 자문가 1명 고용
- Month 2: 투자 유치 or 수익화 계획
```

---

## 팀 및 협력 전략

### 팀 구성

#### 핵심 팀 (MS AI School)

```
1. [귀하]: 아키텍처 설계 + 법리 자문
   - 책임: 전체 시스템 설계, 법리 검증
   - 역할: PM + AI Engineer

2. 팀원 A: NLP/모델 개발
   - 책임: Model 3, 4 구현
   - 역할: ML Engineer

3. 팀원 B: CV/이미지 처리
   - 책임: Model 1, 2 구현
   - 역할: CV Engineer

4. (선택) 팀원 C: 백엔드 개발
   - 책임: FastAPI, 데이터베이스
   - 역할: Backend Engineer
```

### 변리사 협력 전략

#### Phase 1: 제품 방향성 검증 (Month 1)

**협력자**: 변리사 지인 3-5명  
**역할**: 인터뷰 + 피드백

```
일정: 각 1시간 × 3-5회
방식: 온오프라인 (유동적)
보상: 커피값 + 감사 선물

질문:
1. 현재 상표 침해 모니터링 프로세스?
2. 가장 시간 많이 걸리는 부분?
3. 기존 서비스 (MarqVision 등) 경험?
4. 우리 서비스 유용성 평가?
5. 월 예상 가격은?

산출물:
- 사용자 요구사항 문서
- 기능 우선순위
- 초기 고객 피드백
```

#### Phase 2: 데이터 레이블링 협력 (Month 1-2)

**협력자**: 변리사 1-2명  
**역할**: 판례 분석 + 레이블링

```
작업:
1. 판례 30-50건 선정
2. 외관/호칭/관념 점수 (1-10)
3. 최종 침해/비침해 판정
4. 핵심 요소 기술

보상: ₩30만 or 3개월 무료 이용권

산출물:
- 학습 데이터셋 (30-50개)
- 판례 분석 가이드
- 모델 검증 기준
```

#### Phase 3: 베타 테스트 (Month 2-3)

**협력자**: 변리사 5-10명  
**역할**: 실제 사용 + 피드백

```
조건:
- 3개월 무료 사용
- 주 1회 이상 사용 (10-20건)
- 월 1회 피드백 미팅
- "맞음/틀림" 레이블링

혜택:
- 우선 기능 요청권
- 정식 출시 시 50% 할인 (영구)
- 사용자 후기 기재 권리

산출물:
- 사용성 피드백
- 오류 패턴 분석
- 개선 요청사항
- 초기 추천사
```

#### Phase 4: 초기 고객 전환 (Month 3-6)

**목표**: 베타 테스터 → 유료 고객 5-7명

```
전환 전략:
1. 만족도 조사 (Month 3)
2. 유료 플랜 제시 (Month 3 말)
3. 50% 할인 + 무료 온보딩 제공
4. 3개월 후 정가 적용

가격:
- Basic: ₩30만/월 (개인 변리사)
- Pro: ₩80만/월 (중소 로펌)
- Enterprise: 상담

산출물:
- 5-7명 유료 고객
- MRR ₩300-500만
- 추천 후기
```

### 네트워크 확장

#### 레퍼럴 프로그램

```
구조:
- 기존 고객이 친구/동료 소개
- 소개자: 1개월 무료 or ₩10만 할인
- 신규: 첫 달 50% 할인

목표:
- Month 3: 10명 고객
- Month 6: 20-30명 고객
- Year 1: 50명+ 고객
```

#### 협회/학회 연계

```
대상:
- 대한변리사협회 (KIPA)
- 한국지식재산보호협회
- 중소기업 CEO 모임 등

활동:
- 세미나 발표 (무료)
- 웨비나 개최
- 뉴스레터 발행
- 판례 분석 블로그

효과:
- 브랜드 인지도
- 신뢰성 구축
- 초기 고객 확보
```

---

## 성공 기준

### MVP 성공 기준 (Week 6)

```
✅ 기술적
[ ] Model 3 정확도 90%+
[ ] Model 2 정확도 75%+
[ ] Model 4 정확도 60%+
[ ] 통합 F1-score 65-70%
[ ] End-to-end 파이프라인 작동

✅ 비즈니스
[ ] 변리사 5명 이상 인터뷰 완료
[ ] 판례 50개 레이블링 완료
[ ] 베타 테스터 모집 완료

✅ 문서화
[ ] 기술 문서 완성
[ ] API 명세 작성
[ ] README + 사용 가이드
```

### 베타 성공 기준 (Month 3)

```
✅ 기술적
[ ] F1-score 75-80%
[ ] 오탐율 10-15% 이하
[ ] 처리 속도 안정적 (3-5초/건)

✅ 비즈니스
[ ] 베타 테스터 8-10명 확보
[ ] 월간 분석 건수 500+
[ ] NPS (Net Promoter Score) 50+

✅ 고객 피드백
[ ] 사용 만족도 4/5 이상
[ ] 개선 요청사항 정리
[ ] 유료 전환 의사 5-7명
```

### 정식 출시 기준 (Month 4-6)

```
✅ 제품
[ ] F1-score 82-87%
[ ] 웹 대시보드 안정화
[ ] 보고서 자동 생성
[ ] API 제공

✅ 고객
[ ] 유료 고객 5-10명
[ ] MRR ₩300만+
[ ] 확장 레퍼럴 채널 활성화

✅ 마케팅
[ ] 웹사이트 + 블로그
[ ] 기본 마케팅 (이메일, SNS)
[ ] 초기 PR (아티클 등)
```

---

## 부록: 기술 명세

### API 명세 (예시)

```
POST /api/v1/analyze
{
  "base_mark": {
    "image_url": "...",
    "text": "나이키",
    "type": "mixed",
    "nics": ["25"]
  },
  "target_mark": {
    "image_url": "...",
    "text": "니이키",
    "nics": ["25"]
  }
}

Response:
{
  "final_score": 79,
  "risk_level": "Medium Risk",
  "breakdown": {
    "visual": 75,
    "phonetic": 85,
    "conceptual": 30
  },
  "weights": {
    "visual": 0.2,
    "phonetic": 0.6,
    "conceptual": 0.2
  },
  "similar_cases": [
    {
      "case_id": "2023허1234",
      "similarity_to_current": 0.85,
      "judgment": "침해"
    }
  ],
  "recommendation": "경고장 발송 권장"
}
```

### 데이터베이스 스키마 (Simplified)

```sql
-- 사용자 (변리사/로펌)
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(255),
  company_name VARCHAR(255),
  plan VARCHAR(50),  -- Basic/Pro/Enterprise
  created_at DATETIME
);

-- 기준 상표
CREATE TABLE base_marks (
  id INT PRIMARY KEY,
  user_id INT,
  mark_text VARCHAR(255),
  mark_image_url VARCHAR(500),
  mark_type VARCHAR(50),  -- text/logo/mixed
  nics TEXT,  -- JSON array
  created_at DATETIME
);

-- 분석 결과
CREATE TABLE analysis_results (
  id INT PRIMARY KEY,
  user_id INT,
  base_mark_id INT,
  target_mark_text VARCHAR(255),
  target_mark_image_url VARCHAR(500),
  final_score FLOAT,
  risk_level VARCHAR(50),
  visual_score FLOAT,
  phonetic_score FLOAT,
  conceptual_score FLOAT,
  user_feedback VARCHAR(50),  -- correct/incorrect/unsure
  created_at DATETIME
);

-- 피드백 (개선용)
CREATE TABLE feedbacks (
  id INT PRIMARY KEY,
  analysis_id INT,
  user_id INT,
  is_correct BOOLEAN,
  comment TEXT,
  created_at DATETIME
);
```

---

## 결론

TrademarkGuard는 **법리 기반 AI**와 **도메인 전문성**을 결합한 혁신적인 서비스입니다.

### 핵심 강점

1. **고유한 시장 포지셔닝**: 위조품 탐지(MarqVision)와 법적 분석(변리사) 사이의 gap 채우기
2. **우수한 시스템 설계**: 시니어 AI 개발자 수준의 모듈식 아키텍처
3. **강력한 팀 자산**: 법리 지식 + AI 기술 + 변리사 네트워크
4. **명확한 시장 수요**: 변리사 상표 모니터링 업무 3배 효율화

### 성공 가능성

```
기술 (60%) + 시장 (30%) + 팀 (10%) = 100%

- 기술: MVP 70% → 고도화 85-90% (달성 가능)
- 시장: SAM ₩288억, SOM ₩48-96억 (충분함)
- 팀: 변리사 네트워크 + AI 실력 (준비 완료)

→ 성공 확률: 70-80%
```

### 다음 액션

```
이번 주:
[ ] 팀 최종 구성
[ ] 변리사 지인 5명 리스트업
[ ] 개발 환경 설정

다음 주:
[ ] 인터뷰 요청 발송
[ ] 데이터 수집 자동화
[ ] Week 1 개발 시작
```

**시작합시다!** 🚀

---

**문서 작성 완료**  
2026년 1월 9일  
MS AI School 프로젝트 팀
