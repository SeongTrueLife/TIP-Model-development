"""
[Node 0] Score Calibrator (The Normalizer)

Role:
    서로 다른 스케일과 분포를 가진 모델 2, 3, 4의 Raw Score를
    통일된 '유사도(Similarity Probability, 0.0~1.0)'로 변환합니다.
    
Type:
    Python Function (Deterministic, CPU-bound)

Logic:
    Piecewise Linear Interpolation (구간 선형 보간)을 사용하여,
    각 모델별 임계값(Threshold)을 기준으로 점수를 재조정(Re-scale)합니다.
"""

from typing import Dict, List, Tuple, Any, Optional
from ..state import AgentState

# --- [Configuration: Tuning Required] ---
# TODO: [실험 필요] 실제 데이터 테스트 후 아래 임계값(Anchor Points)들을 미세 조정해야 함.
# Format: List of (Raw Score, Target Similarity Score 0.0~1.0)
# 주의: Raw Score 기준으로 오름차순 정렬되어 있어야 함.

# Model 2 (Visual): Cosine Similarity (-1.0 ~ 1.0)
# Team Feedback:
# 0.7 ~ 1.0: 매우 높음 (동일)
# 0.3 ~ 0.7: 보통 (유사, 스타일 변형)
# 0.2 ~ 0.3: 경계 (형태적 유사)
# 0.2 미만: 낮음 (비유사)
VISUAL_ANCHORS: List[Tuple[float, float]] = [
    # [History] Tuning 전 초기값 (Baseline)
    # (-1.0, 0.0), (0.2, 0.1), (0.3, 0.5), (0.7, 0.9), (1.0, 1.0)
    # [Tuning Log: 2026-02-18 Option C 적용]
    # 데이터 분석 결과: Raw Score 0.4~0.7 구간의 실제 유사 확률은 약 48%임.
    # 따라서 0.6점일 때 0.55(Option B)나 0.35(Option A)가 아닌,
    # 실제 확률에 근사하되 살짝 보수적인 0.45점을 부여함.
    # 의도: 애매하면 단독으로는 비유사(0.5 미만) 처리하되, 다른 모델 점수가 높으면 침해로 넘어가도록 유도.
    (0.0, 0.0),
    (0.2, 0.1),  # 0.2 미만은 확실히 아님
    (0.6, 0.45), # [핵심] Gray Zone (실제 유사확률 48%). 0.5 미만으로 억제.
    (0.7, 0.65), # 0.7부터 '가능성 있음' 구간 진입
    (0.8, 0.85), # [확신] 0.8 이상은 확실한 유사
    (1.0, 1.0)
]

# Model 3 (Phonetic): Distance based Score (0 ~ 100)
# Team Feedback:
# 정확도 69~71% (80점 기준일 때 가장 높음)
# 즉, 80점이 넘어가야 신뢰할 수 있는 '유사'임.
PHONETIC_ANCHORS: List[Tuple[float, float]] = [
    #수정함. 배재현님 참고 부탁
    # [History] Tuning 전 초기값 (Baseline)
    # (0.0, 0.0), (50.0, 0.2), (70.0, 0.5), (80.0, 0.85), (100.0, 1.0)
    # [Tuning Log: 2026-02-18 S-Curve 적용]
    # Filtered Data(0점 제외) 기준: 비유사 평균 61점, 유사 평균 80점.
    # 비유사 중앙값이 70점이므로, 70점 초반까지는 점수를 억제(0.55 이하)하고
    # 80점부터 확 높여주는(0.8 이상) S자 곡선 적용.
    (0.0, 0.0),
    (50.0, 0.1), # 50점 이하는 거의 노이즈
    (60.0, 0.3), # 비유사 평균(61점) 지점. 억제.
    (73.0, 0.55), # [변곡점] 73점부터 가능성 구간 진입.
    (80.0, 0.8), # 유사 평균(80점). 확실한 침해.
    (90.0, 0.95), # 거의 동일
    (100.0, 1.0)
]

# Model 4 (Semantic): Cosine Similarity (-1.0 ~ 1.0)
# Team Feedback:
# 0.3 미만: 매우 낮음
# 0.5 ~ 0.59: 가능성 있음 (Medium)
# 0.6 ~ 0.69: 높음 (High)
# 0.7 이상: 매우 높음 (Very High)
SEMANTIC_ANCHORS: List[Tuple[float, float]] = [
    # [History] Tuning 전 초기값 (Baseline)
    # (-1.0, 0.0), (0.4, 0.2), (0.5, 0.5), (0.6, 0.8), (0.7, 0.95), (1.0, 1.0)
    # [Tuning Log: 2026-02-18 Suppress & Stretch 적용]
    # 데이터 분석 결과: 비유사 중앙값(0.64)과 유사 중앙값(0.71)이 매우 근접함.
    # 기존에는 0.6만 넘어도 0.8(유사)을 줬으나, 이는 비유사 데이터 대다수를 오탐하게 만듦.
    # 따라서 0.6~0.7 구간을 강제로 찢어발겨서(Stretch), 0.65까지는 점수를 억제하고 0.75부터 인정함.
    (-1.0, 0.0),
    (0.5, 0.1),  # 하위권 노이즈 제거
    (0.6, 0.2),  # [제재] 비유사 구간. 점수 대폭 삭감.
    (0.65, 0.4), # [경계 1] 비유사 중앙값(0.64) 지점. 아직 비유사.
    (0.7, 0.65), # [경계 2] 유사 중앙값(0.71) 근처. 가능성 열어둠.
    (0.75, 0.85), # [확신] 상위 10% 비유사도 0.73임. 0.75 넘으면 찐유사.
    (1.0, 1.0)
]


def interpolate_score(raw_value: float, anchors: List[Tuple[float, float]]) -> float:
    """
    주어진 raw_value가 anchors의 어느 구간에 속하는지 찾아서 선형 보간(Linear Interpolation)합니다.
    
    Args:
        raw_value (float): 변환할 원본 점수
        anchors (List[Tuple[float, float]]): (Raw, Target) 튜플의 리스트. Raw 기준 오름차순 정렬 필수.
        
    Returns:
        float: 0.0 ~ 1.0 사이의 정규화된 점수
    """
    # 1. 범위 밖 처리 (Clamping)
    if raw_value <= anchors[0][0]:
        return anchors[0][1]
    if raw_value >= anchors[-1][0]:
        return anchors[-1][1]
        
    # 2. 구간 탐색 및 선형 보간
    for i in range(len(anchors) - 1):
        x1, y1 = anchors[i]
        x2, y2 = anchors[i + 1]
        
        if x1 <= raw_value <= x2:
            # Linear Interpolation Formula: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
            # 분모가 0인 경우 방지 (x1 == x2 인 경우)
            if x2 == x1:
                return y1 
            
            ratio = (raw_value - x1) / (x2 - x1)
            interpolated_y = y1 + ratio * (y2 - y1)
            return round(interpolated_y, 4) # 소수점 4자리까지 반올림

    return 0.0 # Should not be reached logic


def score_calibrator(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function
    base_scores를 읽어와서 calibrated_scores로 변환하여 반환합니다.
    """
    
    # 1. 입력 검증 및 기본값 처리
    base_scores = state.get("base_scores")
    if not base_scores:
        # base_scores가 아예 없는 경우 방어 로직 -> 모두 0.0 처리
        return {
            "calibrated_scores": {
                "visual": 0.0,
                "phonetic": 0.0,
                "semantic": 0.0
            }
        }

    # 2. 각 모델별 점수 추출 (없으면 0.0)
    # Model 2,3,4가 항상 모든 키를 준다는 보장이 없으므로 get(key, 0.0) 사용
    raw_vis = base_scores.get("visual", 0.0)
    raw_pho = base_scores.get("phonetic", 0.0)
    raw_sem = base_scores.get("semantic", 0.0)

    # 3. 보간법 적용 (Logic)
    cal_vis = interpolate_score(raw_vis, VISUAL_ANCHORS)
    cal_pho = interpolate_score(raw_pho, PHONETIC_ANCHORS)
    cal_sem = interpolate_score(raw_sem, SEMANTIC_ANCHORS)

    # 4. 결과 반환 (State Update)
    # LangGraph는 반환된 Dict를 기존 State에 병합(Merge)합니다.
    return {
        "calibrated_scores": {
            "visual": cal_vis,
            "phonetic": cal_pho,
            "semantic": cal_sem
        }
    }
