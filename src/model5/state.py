"""
[Model 5] AgentState Definition

이 모듈은 LangGraph 파이프라인 전체에서 공유되는 상태(State) 객체를 정의합니다.
데이터의 흐름을 추적하고, 각 단계(Node) 간의 인터페이스 역할을 수행합니다.
"""
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):

    """
    LangGraph의 모든 노드가 공유하는 데이터 구조체입니다.
    
    Attributes:
        target_img (str): 등록상표 이미지 경로 또는 Base64 문자열.
        target_text (str): 등록상표의 텍스트(문자) 정보.
        target_product (str): 지정상품명 (예: '의류', '화장품').
        base_scores (Dict[str, float]): 이전 모델(Model 2,3,4)들의 Raw Score.
            Example: {"visual": 0.72, "phonetic": 68.0, "semantic": 0.88}
        sem_desc (str): Model 4가 생성한 관념(의미) 묘사 텍스트.
        
        calibrated_scores (Dict[str, float]): [Node 0] 정규화된(0.0~1.0) 위험도 점수.
        vis_desc (str): [Node 1] Agent A가 생성한 시각적 묘사 텍스트.
        rag_queries (Dict[str, Any]): [Node 2] 검색을 위한 쿼리 및 필터 정보.
            Example: {"queries": ["query1", ...], "filter_tags": ["tag1", ...]}
        rag_contexts (List[str]): [Node 3] Vector DB 등에서 검색된 판례/심사지침 본문 리스트.
        
        legal_analysis (Dict[str, Dict[str, Any]]): [Node 4] 식별력 등급 판단 결과.
            Structure:
            {
                "visual": {"grade": "Grade 5", "reason": "..."},
                "phonetic": {"grade": "Grade 2", "reason": "..."},
                ...
            }
        dynamic_weights (Dict[str, float]): [Node 5] 등급에 따라 매핑된 가중치.
            Example: {"visual": 1.0, "phonetic": 0.2, "semantic": 0.05}
            
        final_score (float): [Node 6] 최종 계산된 침해 확률 (0.0 ~ 1.0).
        risk_level (str): [Node 6] 최종 위험 등급 (High / Medium / Low).
        
        report_meta (Dict[str, Any]): [Node 6] 보고서 생성을 위한 메타 데이터.
            판단 근거(Logic Type), 적용된 룰, 계산 경로(Trace) 등을 포함합니다.
    """

    # LangGraph의 상태를 저장하는 TypedDict.
    # 초기 입력값을 제외한 중간 산출물과 최종 결과는 초기화 시점에 None일 수 있으므로 Optional로 정의함.
 
    
    # --- [Initial Inputs] 초기 입력값 (필수) ---
    target_img: str          # 등록상표 이미지 (Base64/Path)
    target_text: str         # 등록상표 텍스트
    target_product: str      # 지정상품 (예: "의류")
    base_scores: Dict[str, float]  # 모델 2,3,4의 Raw Score ({'visual': 0.7, ...})
    sem_desc: str            # 모델 4가 생성한 관념 묘사 텍스트 (외부 주입)

    # --- [Intermediate Artifacts] 중간 산출물 (초기엔 None) ---
    # Node 0: 정규화된 점수 (0.0~1.0)
    calibrated_scores: Optional[Dict[str, float]]
    
    # Node 1: 외관 묘사 텍스트
    vis_desc: Optional[str]
    
    # Node 2: 검색 쿼리 리스트
    rag_queries: Optional[Dict[str, Any]]
    
    # Node 3: 검색된 판례/심사지침 본문 리스트
    rag_contexts: Optional[List[str]]

    # --- [Core Logic Output] 핵심 판단 결과 ---
    # Node 4: 식별력 5등급 및 판단 근거
    # 구조: { "visual": {"grade_label": "...", "grade_score": 5, "reason": "..."}, ... }
    legal_analysis: Optional[Dict[str, Dict[str, Any]]]
    
    # Node 5: 매핑된 가중치 수치
    dynamic_weights: Optional[Dict[str, float]]

    # --- [Final Outputs] 최종 결과 ---
    # Node 6: 최종 침해 확률
    final_score: Optional[float]
    # Node 6: 위험 등급 (High/Medium/Low)
    risk_level: Optional[str]

    # --- [Export Data] 보고서 팀 전달용 ---
    # 판단 근거, 적용된 법리, 계산 경로(Trace) 등
    report_meta: Optional[Dict[str, Any]]
