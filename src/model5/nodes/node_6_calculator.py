"""
[Node 6] Final Calculator (The Math Solver)

Role:
    요부 관찰(Dominant Part Rule)과 전체 관찰(Overall Observation Rule) 로직을 분기하여
    최종 침해 확률(Final Score)과 위험 등급(Risk Level)을 계산합니다.

Type:
    Python Function (Deterministic, CPU-bound)

Logic:
    Case A (요부 관찰): 식별력이 강하고(Weight High) 유사도도 높은(Score High) 부분이 있다면, 그 점수를 채택.
    Case B (전체 관찰): 그렇지 않다면, 가중 평방 평균(Weighted RMS)으로 전체적인 인상을 종합.
"""

import math
from typing import Dict, Any, List, Optional
from ..state import AgentState

# --- [Configuration] ---
# 요부(Dominant Part) 판단 기준
# 요부 판단 기준 미세조정 필요.
THRESHOLD_WEIGHT: float = 0.8  # Grade 4(Strong) 이상
# [Tuning Log: 2026-02-18 Threshold 재설정]
# High Risk 기준(0.7)과 일치시킴. (0.8 -> 0.7)
THRESHOLD_SCORE: float = 0.7   # High Risk (유사도 높음)

# 위험 등급(Risk Level) 분류 기준
# 0.6 미만은 Safe로 간주하여 보고서 대상에서 제외
RISK_THRESHOLDS = {
    # [History] Tuning 전 초기값
    # "HIGH": 0.90,
    # "MEDIUM": 0.75,
    # "CUTOFF": 0.60

    # [Tuning Log: 2026-02-18 Threshold 재설정]
    # 모델의 전반적인 점수 하향 평준화(Suppress 전략)에 맞춰 기준 완화
    "HIGH": 0.70,   # [변경: 0.90 -> 0.70]
    "MEDIUM": 0.55, # [변경: 0.75 -> 0.55]
    "CUTOFF": 0.40  # [변경: 0.60 -> 0.40] Low Risk 마지노선 (Recall 79% 확보)
}

def calculate_weighted_rms(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    가중 평방 평균 (Weighted RMS) 계산
    Formula: sqrt( sum(w * s^2) / sum(w) )
    """
    numerator = 0.0
    denominator = 0.0
    
    for key in scores:
        s = scores.get(key, 0.0)
        w = weights.get(key, 0.0)
        
        # [Logic 2] Missing Value Handling (0점 오류 처리) - 2026-02-18 추가
        # 점수가 0.0인 경우(에러/누락)는 평균 계산에서 아예 배제함.
        if s > 0.001:  # 0.001 미만은 0으로 간주
            numerator += w * (s ** 2)
            denominator += w
        
    if denominator == 0:
        return 0.0
        
    return math.sqrt(numerator / denominator)

def determine_risk_level(score: float) -> str:
    """
    최종 점수에 따른 위험 등급 결정 (Revised Logic)
    - 0.9 이상: High (고위험)
    - 0.75 ~ 0.9: Medium (중위험)
    - 0.6 ~ 0.75: Low (저위험 - 관찰 필요)
    - 0.60 미만: Safe (비유사 - 보고서 제외)
    """
    if score >= RISK_THRESHOLDS["HIGH"]:
        return "High"
    elif score >= RISK_THRESHOLDS["MEDIUM"]:
        return "Medium"
    elif score >= RISK_THRESHOLDS["CUTOFF"]:
        return "Low"
    else:
        return "Safe"

def final_calculator(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function
    """
    
    # 1. 입력 데이터 준비 및 검증
    # 값이 없으면 기본값 0.0으로 처리하여 계산 오류 방지
    raw_scores = state.get("calibrated_scores") or {}
    raw_weights = state.get("dynamic_weights") or {}
    
    keys = ["visual", "phonetic", "semantic"]
    scores = {k: raw_scores.get(k, 0.0) for k in keys}
    weights = {k: raw_weights.get(k, 0.0) for k in keys}
    
    # 2. Trigger Check (요부 관찰 적용 여부 확인)
    # 식별력이 강한데(Weight High) 유사하기까지 한(Score High) 요소가 있는지 탐색
    dominant_factors: List[str] = []
    
    for k in keys:
        if weights[k] >= THRESHOLD_WEIGHT and scores[k] >= THRESHOLD_SCORE:
            dominant_factors.append(k)
            
    # 3. 로직 분기 및 점수 계산
    final_score = 0.0
    logic_type = ""
    message = ""
    
    if dominant_factors:
        # [Case A] Dominant Part Rule (요부 관찰)
        # "하나만 걸려도 아웃이다"
        logic_type = "Dominant_Part_Rule"
        
        # 요부 조건을 만족하는 항목들 중 가장 높은 유사도 점수를 채택
        # 예: 외관(0.9), 호칭(0.85) 둘 다 요부라면 더 높은 0.9가 최종 점수
        max_dominant_score = max([scores[k] for k in dominant_factors])
        final_score = max_dominant_score
        
        message = f"요부(Dominant Part)로 판단된 항목({', '.join(dominant_factors)})의 높은 유사도로 인해 침해 가능성이 높게 판단됨."
        #이부분 나중에 보완 필요. 모델5를 위한것은 아니고 보고서 작성 파트를 위한 것임. 예를 들어 요부 조건을 만족하는 항목이 2 이상일때(예 외관 유사도 점수 0.9, 호칭 유사도 점수 0.92), 가장 높은 유사도 점수를 가진 항목 뿐만 아니라, 다른 항목에 대한 metadata도 넘겨야함. 예를 들어 요부로 판단되는 외관과 호칭 모두가 유사해서 침해 가능성이 높게 판단된다 라든지지
    else:
        # [Case B] Overall Observation Rule (전체 관찰)
        # "전체적인 인상을 종합적으로 본다"
        logic_type = "Overall_Observation_Rule"
        
        final_score = calculate_weighted_rms(scores, weights)
        message = "특정 요부가 발견되지 않아, 외관/호칭/관념을 종합적으로 고려(Weighted RMS)하여 판단함."

        # [Logic 3] Cross-Check (상호 검증) - 2026-02-18 추가 (Revised v2)
        # 조건: 관념 점수가 0.8 이상으로 높고, 최종 점수를 주도하고 있는 상황
        
        # 1차적으로 계산된 점수(final_score: 118L)를 기준으로 판단 (중복 계산 제거)
        temp_final_score = final_score 

        is_semantic_high = (scores["semantic"] >= 0.8) and (scores["semantic"] >= temp_final_score)
        
        # 방어 기제: 0점(Error/Missing)이 발생한 모델은 검사에서 제외하고, 
        # 점수가 존재하는(valid) 나머지 모델들이 모두 낮은지(0.3 미만) 확인.
        other_keys = ["visual", "phonetic"]
        valid_others = [scores[k] for k in other_keys if scores[k] > 0.001] # 0점 제외
        
        # 유효한 점수가 하나라도 있고, 그 점수들이 모두 0.3 미만이어야 함
        if valid_others and all(s < 0.3 for s in valid_others):
            is_others_low = True
        else:
            is_others_low = False

        if is_semantic_high and is_others_low:
            # Action: 원인 제공자인 '관념 점수'만 20% 감점 (Penalty)
            # 이유: 무고한 외관/호칭 점수까지 깎지 않고, 문제의 소지만 정밀 타격함.
            original_sem = scores["semantic"]
            scores["semantic"] *= 0.8 
            
            # 재계산 (Re-calculate)
            final_score = calculate_weighted_rms(scores, weights)
            message += f" [보정] 관념 점수 과다({original_sem} -> {scores['semantic']:.4f})로 인한 패널티 적용 및 재계산."

    # 4. Risk Level 결정
    # 소수점 4자리 반올림 (깔끔한 출력을 위해)
    final_score = round(final_score, 4)
    risk_level = determine_risk_level(final_score)
    
    # 5. 결과 반환 (State Update)
    return {
        "final_score": final_score,
        "risk_level": risk_level,
        "report_meta": {
            "logic_type": logic_type,
            "dominant_factors": dominant_factors,
            "final_score_raw": final_score,
            "message": message,
            "trace_data": {
                "scores_used": scores,
                "weights_used": weights
            }
        }
    }
