"""
[Node 5] Weight Mapper (The Clerk)

Role:
    Node 4(Legal Judge)가 판단한 '식별력 등급(Grade 1~5)'을
    계산 가능한 '가중치(Weight, 0.05~1.0)'로 변환합니다.

Type:
    Python Function (Deterministic, CPU-bound)

Logic:
    Deterministic Mapping Table을 사용하여 등급별 가중치를 부여합니다.
    LLM의 출력이 없거나 오류가 있을 경우, 방어적으로 기본값을 할당합니다.
"""

from typing import Dict, Any, Optional
from ..state import AgentState

# --- [Configuration] ---
# 식별력 등급(Grade)에 따른 가중치(Weight) 매핑
# Grade 1 (식별력 없음) -> 0.05 (완전 0이 아닌 최소값, 연산 오류 방지)
# Grade 5 (독점적 식별력) -> 1.0
# 등급별 가중치 미세조정 필요.
GRADE_WEIGHT_MAP: Dict[int, float] = {
    5: 1.0,  # Exclusive / 독점적
    4: 0.8,  # Strong / 강함
    # [History] Tuning 전 초기값
    # 3: 0.5,  # Moderate / 보통
    
    # [Tuning Log: 2026-02-18 Grade 3 상향]
    # 데이터 분석 결과: 호칭 모델의 경우 '유사(Similar)' 케이스가 Grade 3를 받는 비율이 압도적으로 높음(71%).
    # 따라서 Grade 3의 가중치를 0.5에서 0.6으로 상향하여, 애매하게 유사한 케이스들의 점수를 보존함.
    # 비유사 케이스의 점수 상승 부작용은 Node 0의 Suppress 전략으로 상쇄 가능.
    3: 0.6,  # Moderate / 보통 [변경: 0.5 -> 0.6]
    
    2: 0.2,  # Weak / 약함
    1: 0.05  # None / 없음 (관용표장 등)
}

# 분석 데이터 누락 시 사용할 기본 가중치 (보수적 접근: 보통 수준)
# [Note] Grade 3 가중치 상향에 맞춰 기본값도 0.6으로 맞출지 고민했으나, 
# 데이터가 없는 불확실한 상황에서는 보수적으로 0.5 유지.
DEFAULT_WEIGHT: float = 0.5 

def weight_mapper(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function
    legal_analysis의 grade_score를 dynamic_weights로 변환합니다.
    """
    
    # 1. 입력 검증
    legal_analysis = state.get("legal_analysis")
    
    # 분석 결과가 아예 없는 경우 -> 모든 가중치를 기본값으로 설정
    if not legal_analysis:
        return {
            "dynamic_weights": {
                "visual": DEFAULT_WEIGHT,
                "phonetic": DEFAULT_WEIGHT,
                "semantic": DEFAULT_WEIGHT
            }
        }

    # 2. 각 요소별 가중치 매핑
    dynamic_weights: Dict[str, float] = {}
    target_keys = ["visual", "phonetic", "semantic"]

    for key in target_keys:
        # 각 요소의 분석 결과 가져오기 (없으면 빈 딕셔너리)
        analysis_item = legal_analysis.get(key, {})
        
        # grade_score 추출 (기본값: 3)
        # LLM이 3.0(float)이나 "3"(str)을 줄 수도 있으므로 안전하게 int 변환 시도
        raw_grade = analysis_item.get("grade_score", 3)
        
        try:
            grade_int = int(raw_grade)
        except (ValueError, TypeError):
            grade_int = 3 # 변환 실패 시 중간값
            
        # 매핑 테이블 조회 (1~5 범위를 벗어나면 기본값 처리)
        weight = GRADE_WEIGHT_MAP.get(grade_int, DEFAULT_WEIGHT)
        
        dynamic_weights[key] = weight

    # 3. 결과 반환 (State Update)
    return {
        "dynamic_weights": dynamic_weights
    }
