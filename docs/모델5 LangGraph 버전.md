# [Model 5] LangGraph 아키텍처 최종 명세서 (Final Spec)

## 1. 데이터 파이프라인의 척추: AgentState 정의

모든 노드가 공유하고 업데이트할 데이터 구조입니다.

```python
from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    # --- [Initial Inputs] 초기 입력값 ---
    target_img: str            # 등록상표 이미지 (Base64/Path)
    target_text: str           # 등록상표 텍스트 (보고서용)
    target_product: str        # 지정상품 (예: "의류")
    base_scores: Dict[str, float] # 모델 2,3,4의 Raw Score
    sem_desc: str              # 모델 4가 생성한 관념 묘사 텍스트

    # --- [Intermediate Artifacts] 중간 산출물 ---
    calibrated_scores: Dict[str, float] # [Node 0] 정규화된 점수 (0.0~1.0)
    vis_desc: str              # [Node 1] Agent A의 외관 묘사
    rag_queries: Dict[str, Any]     # [Node 2] 검색 쿼리 리스트
    rag_contexts: List[str]    # [Node 3] 검색된 판례 본문

    # --- [Core Logic Output] 핵심 판단 결과 ---
    legal_analysis: Dict[str, Dict] # [Node 4] 식별력 5등급 및 판단 근거(Reason)
    dynamic_weights: Dict[str, float] # [Node 5] 매핑된 가중치 수치

    # --- [Final Outputs] 최종 결과 ---
    final_score: float         # [Node 6] 최종 침해 확률
    risk_level: str            # [Node 6] 위험 등급 (High/Medium/Low)

    # --- [Export Data] 보고서 팀 전달용 ---
    report_meta: Dict[str, Any] # 판단 근거, 적용된 법리, 계산 경로(Trace) 포함
```

## 2. 노드별 상세 명세 (Node Specification)

### 🟦 Phase 1: 전처리 및 데이터 정규화 (Preprocessing)

#### Node 0: score_calibrator (The Normalizer)

- **역할**: 서로 다른 스케일과 분포를 가진 모델 2, 3, 4의 점수를 통일된 **'유사도 점수'**로 변환합니다.
- **Type**: Python Function (LLM 미사용)
- **입력 (Input)**:
  - `base_scores` (Dict): `{ "visual": 0.72, "phonetic": 68.0, "semantic": 0.88 }`
- **내부 로직 (Logic)**: Piecewise Linear Interpolation (구간 선형 보간)
  - 각 모델의 특성에 맞는 **Anchor Point(기준점)**를 설정하여 0.0~1.0 사이로 매핑합니다.
  - **Mapping Table**:
    - **Model 2 (Visual)**: Raw 0.7 → Risk 0.8 (임계값)
    - **Model 3 (Phonetic)**: Raw 70 → Risk 0.8 (임계값) / 50 → 0.5
    - **Model 4 (Semantic)**: Raw 0.85 → Risk 0.8 (임계값) / 0.6 → 0.2
- **출력 (Output)**:
  - `calibrated_scores` (Dict): `{ "visual": 0.82, "phonetic": 0.78, "semantic": 0.85 }`
- **핵심 결정 사유**: LLM이 판단하기 전에 수학적 기준을 통일해야 후속 판단의 오류를 줄일 수 있음.

### 🟦 Phase 2: 시각적 분석 및 검색 전략 수립 (Analysis & Retrieval)

#### Node 1: visual_describer (Agent A)

- **역할**: 모델 2(Embedding)가 놓치는 구체적인 기하학적 형상, 배치, 색상을 언어화합니다.
- **Type**: LLM (GPT-5.1)
- **입력 (Input)**:
  - `target_img` (Image): 등록상표 이미지
- **내부 로직 (System Prompt)**:
  - **Constraint (제약)**: "주관적 해석 금지, 객관적 묘사 집중."
    - "사자처럼 보인다"(X) → "갈기가 있는 네 발 짐승 형상, 꼬리가 우측으로 말려 올라감"(O)
    - 식별력 유무 판단 절대 금지.
- **출력 (Output)**:
  - `vis_desc` (String): "검은색 테두리의 원형 안에 고딕체로 'ABC'가 기재되어 있으며..."

#### Node 2: query_generator (Search Planner)

- **역할**: RAG 검색 효율을 극대화하기 위한 최적의 검색어(Query)와 필터(Filter)를 생성합니다.
- **Type**: LLM (GPT-4o-mini) (속도 및 비용 최적화)
- **입력 (Input)**:
  - `vis_desc` (Node 1 Output)
  - `sem_desc` (Model 4 Output: 관념 묘사)
  - `target_product` (지정상품)
  - `target_text` (상표명)
- **내부 로직 (Logic)**:
- 1. **Literal**: 상표명 그 자체나 분할된 단어. 혹은 외관이나 관념 묘사
- 2. **Semantic**: 상표의 구조적/추상적 특징 설명문.
- 3. **Category**: 지정상품과 관련된 대표 키워드.

- **Output (JSON Example):**
  - `rag_queries` (Dict[str, Any]): 검색용 쿼리 리스트

```json
{
  "queries": [
    "맛있는 우유 식별력", // Literal: 상표명 자체/포함 단어
    "형용사 수식어와 보통명칭 결합 표장", // Semantic Pattern: 추상적 구조
    "유제품 성질표시 거절 사례" // Category: 지정상품군 내 기준
  ],
  "filter_tags": ["TAG_성질표시", "CLS_식품"]
}
```

#### Node 3: legal_retriever (The Librarian)

- **역할**: 유사 심사지침 및 판례 데이터를 검색합니다.
- **Type**: Vector DB Search (SQL => 질문-팀원에게)
- **입력 (Input)**:
  - `rag_queries`
- **내부 로직 (Logic)**: Hybrid Search (Vector + Soft Filter)
  - **Vector Search**: 쿼리와 문맥적으로 유사한 판례 검색.
  - **Metadata Filter**: 지정상품 카테고리가 일치하면 가산점(Boost) 부여, 불일치해도 검색 결과에는 포함(유사 법리 적용 가능성 때문).
- **출력 (Output)**:
  - `rag_contexts` (List[Document]): 검색된 특허청 거절이유서 본문 및 메타데이터 리스트.

### 🟦 Phase 3: 법리적 판단 및 의사결정 (Reasoning & Decision)

#### Node 4: legal_judge (Agent B)

- **역할**: 판례와 상표 정보를 종합하여 **식별력 등급(5-Tier)**을 판정하고 **근거(Reason)**를 서술합니다. (사실상 가장 중요한 뇌)
- **Type**: LLM (GPT-5.1) (High Reasoning Capability)
- **입력 (Input)**:
  - `calibrated_scores` (점수 확인용)
  - `vis_desc`, `sem_desc` (상표 특징)
  - `target_img`, `target_text`(상표 정보)
  - `target_product` (지정상품)
  - `rag_contexts` (법리 기준)
- **내부 로직 (Prompting Strategy)**:
  - **Task**: 각 요소(외관, 호칭, 관념)에 대해 5단계 등급 중 하나를 선택하라.
  - **Reference**: RAG로 검색된 판례를 근거로 삼아라. (예: "판례 A에서 '맛있는'은 식별력 없음으로 보았으므로...")
  - **Constraint**: 요부의 위치를 찍으려 하지 말고, **등급(Grade)**으로만 표현하라.
- **등급**
  - Grade 5 (Exclusive / 독점적) : 조어(지어낸 말), 매우 독창적인 도안.
  - Grade 4 (Strong / 강함) : 흔하지 않은 단어, 독특한 결합.
  - Grade 3 (Moderate / 보통) : 암시적(Suggestive)이지만 직감적이진 않음.
  - Grade 2 (Weak / 약함) : 성질표시, 흔한 표장, 간단한 도형.
  - Grade 1 (None / 없음) : 관용표장, 보통명칭, 식별 불가능.
- **출력 (Output)**: `legal_analysis` (JSON)

```json
{
  "visual": {
    "grade": "Grade 5 (Exclusive)",
    "reason": "기하학적 도형이 매우 독창적이며..." // 보고서 팀 전달용
  },
  "phonetic": { "grade": "Grade 2 (Weak)", "reason": "..." },
  "semantic": { "grade": "Grade 1 (None)", "reason": "..." }
}
```

#### Node 5: weight_mapper (The Clerk)

- **역할**: Node 4의 언어적 등급 평가를 계산 가능한 수치(Float)로 변환합니다.
- **Type**: Python Function (LLM 미사용)
- **입력 (Input)**:
  - `legal_analysis`
- **내부 로직 (Logic)**: Deterministic Mapping Table
  - Grade 5 (Exclusive / 독점적) → 1.0
  - Grade 4 (Strong / 강함) → 0.8
  - Grade 3 (Moderate / 보통) → 0.5
  - Grade 2 (Weak / 약함) → 0.2
  - Grade 1 (None / 없음) → 0.05 (0으로 인한 연산 오류 방지)
- **출력 (Output)**:
  - `dynamic_weights` (Dict): `{ "visual": 1.0, "phonetic": 0.2, "semantic": 0.05 }`

#### Node 6: final_calculator (The Math Solver)

- **역할**: 최종 점수 계산 및 리포트용 로그 생성.
- **Type**: Python Function (LLM 미사용)
- **입력 (Input)**:
  - `calibrated_scores` (from Node 0)
  - `dynamic_weights` (from Node 5)
- **내부 로직 (Logic)**: Conditional Branching (분기 로직)
  - **Step 1: Check Case A (Dominant Part Rule - 요부관찰)**
    - 조건: `(Weight >= 0.8 AND Score >= 0.8)`인 항목이 존재하는가?
    - True: `Final Score = Max(Scores)`
    - Logic Name: `Dominant_Part_Rule`
  - **Step 2: Check Case B (Overall Observation Rule - 전체관찰)**
    - False (위 조건 불만족): `Final Score = Weighted RMS`
    - Logic Name: `Overall_Observation_Rule`
  - **Step 3: Generate Trace**
    - 어떤 로직을 탔고, 어떤 가중치가 핵심이었는지 기록.
- **출력 (Output)**:
  - `final_score` (Float): 최종 침해 확률 (0.0~1.0)
  - `risk_level` (String): High / Medium / Low
  - `report_meta` (JSON): 보고서 팀 전달용 데이터

  - **[Case A: 요부 관찰이 적용된 경우]**

"하나만 걸려도 아웃이다"

```json
"report_meta": {
    "logic_type": "Dominant_Part_Rule",  # 핵심 분기점
    "trigger_factor": "Visual",          # 범인(요부)은 외관이다
    "dominant_score": 0.92,              # 그놈의 점수
    "dominant_weight": 1.0,              # 그놈의 가중치
    "message": "외관의 식별력이 매우 높아(Grade 5), 외관 유사도만으로 침해를 판단함."
}
```

- **[Case B: 전체 관찰이 적용된 경우]**

"전체적인 인상을 종합적으로 본다"

```json
"report_meta": {
    "logic_type": "Overall_Observation_Rule", # 핵심 분기점
    "factors": {                              # 종합 선물세트
        "visual": {"score": 0.4, "weight": 0.2},
        "phonetic": {"score": 0.6, "weight": 0.5},
        "semantic": {"score": 0.2, "weight": 0.1}
    },
    "final_rms_score": 0.45,
    "message": "특정 요부가 발견되지 않아, 외관/호칭/관념을 가중 평균(RMS)하여 산출함."
}
```

- **Node 6 자세한 수학 수식 설명**

##### Node 6: Final Calculator Mathematical Logic

**1. 변수 정의 (Definitions)**

- $i$: 요소 인덱스 ($\{vis, pho, sem\}$)
- $S'_{i}$: Node 0에서 정규화된 점수 (Calibrated Score)
- $W_{i}$: Node 5에서 매핑된 가중치 (Dynamic Weight)
- $T_{w}$: 가중치 임계값 ($0.8$) → _Grade 4(Strong) 이상_
- $T_{s}$: 점수 임계값 ($0.8$) → _Risk Level High 이상_

**2. 분기 조건 (Branching Condition)**
$$\text{Trigger} = \exists i \text{ s.t. } (W_i \ge T_{w}) \land (S'_i \ge T_{s})$$
_(해석: 식별력이 강하면서(요부) 동시에 점수도 높은 항목이 하나라도 존재하는가?)_

---

**[Case A] 요부 관찰 (Dominant Part Rule)**
_If Trigger is **True**:_

$$Final Score = \max(\{ S'_i \mid (W_i \ge T_{w}) \land (S'_i \ge T_{s}) \})$$

_(해석: 요부 요건을 충족하는 항목들 중 **최댓값**을 최종 침해 확률로 채택)_

---

**[Case B] 전체 관찰 (Overall Observation Rule)**
_If Trigger is **False**:_

$$Final Score = \sqrt{ \frac{W_{vis} \cdot (S'_{vis})^2 + W_{pho} \cdot (S'_{pho})^2 + W_{sem} \cdot (S'_{sem})^2}{W_{vis} + W_{pho} + W_{sem}} }$$

_(해석: **가중 평방 평균 (Weighted RMS)**. 단순 가중 평균보다 높은 점수에 더 큰 페널티를 부여하여, 낮은 점수들이 위험도를 희석(Dilution)시키는 것을 방지)_

## 3. 전체 데이터 흐름도 (Mermaid)

-> 피드백 흐름도 개선을 해야됨. 예를들어 노드0과 노드1은 굳이 직렬로 연결해 둘 필요 없긴함.
-> 나중에 엣지 관련해서 다시 한번 짜기.

```mermaid
graph TD
    %% 초기화 및 전처리
    START(Input Data) --> N0[Node 0: Score Calib]
    START(Input Data) --> N1[Node 1: Vis Desc]

    %% 병렬 실행 후 합류 (Join)
    N0 --> JOIN(State Update)

    %% Node 0의 결과는 State에 저장되어 있다가 나중에 Node 4, 6에서 쓰임
    JOIN -.-> N4

    %% RAG 검색 파이프라인
    N1 --> N2[Node 2: Query Generator<br/>(LLM: Mini)]
    N2 --> N3[Node 3: Legal Retriever<br/>(Vector DB)]

    %% 핵심 법리 판단 (Reasoning)
    N3 --> N4[Node 4: Legal Judge<br/>(LLM: GPT-5.1)]
    %% 입력: Calibrated Score, Vis Desc, Sem Desc, RAG Context

    %% 수치 변환 및 최종 계산 (Deterministic)
    N4 --> N5[Node 5: Weight Mapper<br/>(Python)]
    N5 --> N6[Node 6: Final Calculator<br/>(Python)]

    %% 결과 출력
    N6 --> END(Final Report & Data Export)

    style N0 fill:#f9f,stroke:#333
    style N5 fill:#f9f,stroke:#333
    style N6 fill:#f9f,stroke:#333
    style N4 fill:#bbf,stroke:#333
```
