# Model 5 Performance Analysis Report

## 1. Executive Summary
This report analyzes the performance of Model 5 on the test dataset `baseline_result_test_final_real_version.csv`. 
We evaluated three different decision thresholds to determine the optimal configuration for the "Similar" (Infringement) class:

*   **Low+**: Risk Level `Low`, `Medium`, or `High` considered as Similar.
*   **Medium+**: Risk Level `Medium` or `High` considered as Similar.
*   **High**: Only Risk Level `High` considered as Similar.

**Key Finding**: The **Low+ threshold** achieves the best overall performance with **80.67% Accuracy** and **91.8% Recall**.

## 2. Detailed Metrics

| Metric | Low+ (Aggressive) | Medium+ (Balanced) | High (Conservative) |
| :--- | :--- | :--- | :--- |
| **Accuracy** | **0.8067** | 0.7867 | 0.7200 |
| **Precision** | 0.7000 | 0.7377 | **0.7436** |
| **Recall** | **0.9180** | 0.7377 | 0.4754 |
| **F1-Score** | **0.7943** | 0.7377 | 0.5800 |

*   **Low+**: Best for "Detection". Covers most overlapping cases (High Recall) but has slightly more False Positives.
*   **Medium+**: Balanced approach.
*   **High**: Best for "Validation". Very conservative, misses half of actual similar cases (Low Recall).

## 3. Confusion Matrices

### Scenario 1: Low+ Threshold (Risk >= Low)
*Criteria: If model predicts Low, Medium, or High -> "Similar"*

![Confusion Matrix - Low+](analysis_images/cm_Low+_threshold.png)

### Scenario 2: Medium+ Threshold (Risk >= Medium)
*Criteria: If model predicts Medium or High -> "Similar"*

![Confusion Matrix - Medium+](analysis_images/cm_Medium+_threshold.png)

### Scenario 3: High Threshold (Risk Only High)
*Criteria: If model predicts High -> "Similar"*

![Confusion Matrix - High](analysis_images/cm_High_threshold.png)

## 4. Conclusion & Recommendation
Based on the current test results, **Model 5 performs best with the 'Low' threshold** included as a positive indicator. 
The **Low+** setting captures **91.8%** of actual infringement cases, which is crucial for a trademark monitoring system where missing a similar trademark (False Negative) is more critical than a false alarm.
