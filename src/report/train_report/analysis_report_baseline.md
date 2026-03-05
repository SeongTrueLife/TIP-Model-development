# 베이스라인 모델 성능 분석 보고서
**분석 일시:** 2026-02-18
**총 데이터 수:** 149건

## Low 기준 (High+Medium+Low)
- **유사(침해) 판정 기준:** Risk Level이 ['High', 'Medium', 'Low'] 중 하나일 때

| 카테고리 | 데이터 수 | 정확도(Accuracy) | 정밀도(Precision) | 재현율(Recall) | F1-Score | 오분류(Confusion) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 62 | 0.7419 | 1.0000 | 0.7419 | 0.8519 | TN=0, FP=0, FN=16, TP=46 |
| Case Law (Dissimilar) | 37 | 0.4865 | 0.0000 | 0.0000 | 0.0000 | TN=18, FP=19, FN=0, TP=0 |
| Easy Negative | 50 | 0.8600 | 0.0000 | 0.0000 | 0.0000 | TN=43, FP=7, FN=0, TP=0 |
| **전체 (Overall)** | 149 | 0.7181 | 0.6389 | 0.7419 | 0.6866 | TN=61, FP=26, FN=16, TP=46 |

---

## Medium 기준 (High+Medium)
- **유사(침해) 판정 기준:** Risk Level이 ['High', 'Medium'] 중 하나일 때

| 카테고리 | 데이터 수 | 정확도(Accuracy) | 정밀도(Precision) | 재현율(Recall) | F1-Score | 오분류(Confusion) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 62 | 0.5806 | 1.0000 | 0.5806 | 0.7347 | TN=0, FP=0, FN=26, TP=36 |
| Case Law (Dissimilar) | 37 | 0.6486 | 0.0000 | 0.0000 | 0.0000 | TN=24, FP=13, FN=0, TP=0 |
| Easy Negative | 50 | 0.9400 | 0.0000 | 0.0000 | 0.0000 | TN=47, FP=3, FN=0, TP=0 |
| **전체 (Overall)** | 149 | 0.7181 | 0.6923 | 0.5806 | 0.6316 | TN=71, FP=16, FN=26, TP=36 |

---

## High 기준 (High only)
- **유사(침해) 판정 기준:** Risk Level이 ['High'] 중 하나일 때

| 카테고리 | 데이터 수 | 정확도(Accuracy) | 정밀도(Precision) | 재현율(Recall) | F1-Score | 오분류(Confusion) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 62 | 0.3387 | 1.0000 | 0.3387 | 0.5060 | TN=0, FP=0, FN=41, TP=21 |
| Case Law (Dissimilar) | 37 | 0.8378 | 0.0000 | 0.0000 | 0.0000 | TN=31, FP=6, FN=0, TP=0 |
| Easy Negative | 50 | 0.9600 | 0.0000 | 0.0000 | 0.0000 | TN=48, FP=2, FN=0, TP=0 |
| **전체 (Overall)** | 149 | 0.6711 | 0.7241 | 0.3387 | 0.4615 | TN=79, FP=8, FN=41, TP=21 |

---

## Node 0 정규화 점수 분포 (Calibration Analysis)
각 카테고리별 Node 0 출력값 분포입니다. (Target: 유사=높음, 비유사=낮음)

### 외관(Visual) 점수 분포
| 카테고리 | 평균 (Mean) | 표준편차 (Std) | 최소 (Min) | 최대 (Max) |
| :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 0.6072 | 0.3479 | 0.0833 | 0.9934 |
| Case Law (Dissimilar) | 0.5282 | 0.3491 | 0.0833 | 0.9741 |
| Easy Negative | 0.4738 | 0.3500 | 0.0833 | 0.9831 |

### 호칭(Phonetic) 점수 분포
| 카테고리 | 평균 (Mean) | 표준편차 (Std) | 최소 (Min) | 최대 (Max) |
| :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 0.4644 | 0.4395 | 0.0000 | 1.0000 |
| Case Law (Dissimilar) | 0.2959 | 0.3797 | 0.0000 | 1.0000 |
| Easy Negative | 0.0282 | 0.0477 | 0.0000 | 0.1976 |

### 관념(Semantic) 점수 분포
| 카테고리 | 평균 (Mean) | 표준편차 (Std) | 최소 (Min) | 최대 (Max) |
| :--- | :--- | :--- | :--- | :--- |
| Case Law (Similar) | 0.8866 | 0.1303 | 0.3844 | 0.9727 |
| Case Law (Dissimilar) | 0.7742 | 0.2231 | 0.1962 | 0.9608 |
| Easy Negative | 0.3560 | 0.1550 | 0.1830 | 0.6648 |

