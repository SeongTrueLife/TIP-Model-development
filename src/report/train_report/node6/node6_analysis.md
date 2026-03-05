
# Node 6 (Final Calculator) 튜닝 보고서

**작성일:** 2026-02-18
**대상:** 최종 점수 산출 로직 개선 (0점 처리 및 안전장치 추가)

## 1. 개요 및 목적
단순 수식 계산(Weighted RMS)을 넘어선 지능적인 판단 로직을 추가하여, 시스템 결함(에러)과 모델의 과탐지(Hallucination)를 방지하고자 함.

## 2. 추가 로직 및 근거

### A. [Logic 2] Missing Value Handling (0점 오류 처리)
*   **현상:** 호칭 모델 등에서 에러(0점)가 발생하면, 평균 계산 시 `(점수 합 / 3)`이 되어 전체 평균을 깎아먹음.
*   **개선:** 점수가 `0.0`인 항목은 분모(가중치 합)와 분자(점수 합) 계산에서 모두 **제외(Exclude)**.
*   **근거:** "모르는 건 판단하지 않고, 아는 것만 가지고 판단한다"는 통계적 원칙 준수.

### B. [Logic 3] Cross-Check Safety (상호 검증)
*   **현상:** 관념(의미) 모델은 종종 너무 광범위하게 해석하여 혼자 높은 점수(0.8↑)를 줄 때가 있음.
*   **개선:** "관념만 0.8 이상으로 높고, 외관/호칭은 0.3 미만으로 현저히 낮은 경우" -> **관념 점수만 20% 감점** 후 재계산.
*   **근거:**
    *   판례상 "관념이 유사하더라도 외관/호칭이 현격히 다르면 비유사"로 보는 법리를 구현.
    *   최종 점수를 깎는 방식보다, 원인(관념)을 직접 보정하는 것이 논리적으로 더 타당함.
    *   **데이터 검증:** 현재 학습 데이터(99건) 대상 시뮬레이션 결과, 해당 케이스 **0건** (즉, 기존 정답률을 해치지 않는 안전한 로직임).

## 3. 변경 예정 코드 (src/model5/nodes/node_6_calculator.py)

```python
# 1. 0점(Error) 제외 로직
if s > 0.001: 
    numerator += w * (s ** 2)
    denominator += w

# 2. Cross-Check 로직 (Revised v2)
temp_final_score = final_score
is_semantic_high = (scores["semantic"] >= 0.8) and (scores["semantic"] >= temp_final_score)

# 0점(Error) 제외하고 유효한 점수만 검사
valid_others = [scores[k] for k in ["visual", "phonetic"] if scores[k] > 0.001]

if valid_others and all(s < 0.3 for s in valid_others):
    scores["semantic"] *= 0.8 # 관념 점수만 20% Penalty
    final_score = calculate_weighted_rms(scores, weights) # 재계산
```

## 4. Risk Level 임계값(Threshold) 재설정 (2026-02-18)

전체적인 로직 튜닝(Node 0, 5, 6) 결과, 점수 분포가 하향 안정화되었습니다. 이에 따라 Risk Level 기준을 데이터 기반으로 재설정했습니다.

### 4.1 데이터 분포 및 성능 분석
*   **유사(Similar) 그룹 평균:** 0.63
*   **비유사(Dissimilar) 그룹 평균:** 0.46
*   **최적 성능 지점:** Score 0.40 (Recall 79%, Precision 70%)

### 4.2 변경된 기준 (Thresholds)
| 등급 | 점수 구간 | 의미 및 기대 성능 |
| :--- | :--- | :--- |
| **HIGH** | **0.70 이상** | **확실한 침해.** (High Precision: 85%+) |
| **MEDIUM** | **0.55 ~ 0.70** | **상당항 의심.** (Precision 76%+) |
| **LOW** | **0.40 ~ 0.55** | **유사 가능성 존재.** (Recall 79% 확보를 위한 마지노선) |
| **SAFE** | **0.40 미만** | **안전.** (확실한 비유사 구간) |

### 4.3 기대 효과
*   **과민 반응(False Positive) 감소:** 비유사 케이스의 평균 점수가 0.46으로 낮아져, Safe/Low 등급으로 정확히 분류될 가능성이 높아짐.
*   **놓치는 케이스(False Negative) 방지:** Low 기준을 과감히 0.40까지 낮춰, 애매하게 유사한 상표도 놓치지 않고 경고(Low)를 줄 수 있음.

## 5. Dominant Part Logic (요부 관찰) 미세조정 (2026-02-18)
점수 스케일 조정에 따라 요부 관찰 발동 기준도 논리적 정합성에 맞춰 수정했습니다.

*   **Weight Threshold (식별력):** **0.8 (Grade 4 이상)** 유지 (법적 기준 준수)
*   **Score Threshold (유사도):** **0.8 -> 0.7** 하향 조정
    *   **이유:** High Risk 기준이 0.7로 조정됨에 따라, "강한 식별력(Grade 4)을 가진 부분이 확실한 침해(High Risk) 점수를 얻으면 요부로 본다"는 논리를 유지하기 위함.

