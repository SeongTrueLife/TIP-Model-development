"""
evaluate.py - Golden Set 평가 자동화 v5.6.2
=========================================
Update: 
1. Cross-Validation Support & Report Header Sync
2. Fragment Filtering Logic for Batch Evaluation
"""

import os
import sys
import pandas as pd
import time

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, CODE_DIR)

import converter
import scorer

def run_evaluation():
    input_path = os.path.join(BASE_DIR, "data", "goldenset.xlsx")
    output_path = os.path.join(BASE_DIR, "data", "report.xlsx")
    
    if not os.path.exists(input_path):
        return print(f"❌ 파일을 찾을 수 없습니다: {input_path}")

    # 1. 골든셋 로드
    df = pd.read_excel(input_path)
    report_data = []

    print(f"🚀 [START] 총 {len(df)}건의 골든셋 평가를 시작합니다.")

    for idx, row in df.iterrows():
        brand_a = str(row['brand_a']).strip()
        brand_b = str(row['brand_b']).strip()
        ground_truth = int(row['ground_truth'])
        
        # 2. 복수 발음 변환 로직 호출
        pair = converter.convert_pair(brand_a, brand_b)
        list_a = pair["korean_a"]
        list_b = pair["korean_b"]
        
        # ✅ [핵심 추가] 파편 발음 필터링 (Batch Evaluation 전용)
        # 후보군 중 가장 긴 발음 길이의 80% 이상인 것만 유효한 비교 대상으로 한정
        max_len_a = max(len(p) for p in list_a)
        max_len_b = max(len(p) for p in list_b)
        valid_a = [p for p in list_a if len(p) >= max_len_a * 0.8]
        valid_b = [p for p in list_b if len(p) >= max_len_b * 0.8]
        
        # 3. 모든 발음 조합 중 최적 점수 탐색 (교차 검증)
        best = {"score": -1.0, "p_a": "", "p_b": "", "case": ""}
        
        for p_a in valid_a:
            for p_b in valid_b:
                score, _, case = scorer.compare(p_a, p_b)
                if score > best["score"]:
                    best.update({"score": score, "p_a": p_a, "p_b": p_b, "case": case})
        
        # 4. 판정 및 일치 여부 확인 (임계치 80.0)
        prediction = 1 if best["score"] >= 80 else 0
        is_correct = (prediction == ground_truth)
        
        case_verdict = "침해" if ground_truth == 1 else "비침해"
        model_verdict = "침해" if prediction == 1 else "비침해"
        reason_text = str(row.get('reason', '')).strip() if pd.notna(row.get('reason', '')) else ""
        
        # 5. 결과 리스트 구성 (직관적 헤더 유지)
        report_data.append({
            "No.": idx + 1,
            "원본_상표A": brand_a,
            "원본_상표B": brand_b,
            "AI변환_발음A": best["p_a"],
            "AI변환_발음B": best["p_b"],
            "유사도_점수": round(best["score"], 2),
            "스코어링_로직": best["case"],
            "판례_판결": case_verdict,
            "모델_판단": model_verdict,
            "판례와_일치여부": "✓ 일치" if is_correct else "✗ 불일치",
            "판례_판결근거": reason_text
        })
        
        status = "✓" if is_correct else "✗"
        print(f"[{idx+1:3d}] {brand_a} vs {brand_b} → {best['p_a']} vs {best['p_b']} ({best['score']:.1f}) | 판례:{case_verdict} | 모델:{model_verdict} [{status}]")
        time.sleep(0.1)

    # 6. report.xlsx로 저장
    result_df = pd.DataFrame(report_data)
    result_df.to_excel(output_path, index=False)
    
    # 7. 통계 출력
    total = len(report_data)
    correct = sum(1 for r in report_data if "✓" in r["판례와_일치여부"])
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    tp = sum(1 for r in report_data if r["모델_판단"] == "침해" and r["판례_판결"] == "침해")
    tn = sum(1 for r in report_data if r["모델_판단"] == "비침해" and r["판례_판결"] == "비침해")
    fp = sum(1 for r in report_data if r["모델_판단"] == "침해" and r["판례_판결"] == "비침해")
    fn = sum(1 for r in report_data if r["모델_판단"] == "비침해" and r["판례_판결"] == "침해")
    
    precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0
    recall = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    
    print("\n" + "=" * 60)
    print("[FINAL RESULT] v5.6.2 평가 통계")
    print("=" * 60)
    print(f"   Accuracy: {accuracy:.2f}% ({correct}/{total})")
    print(f"   Precision: {precision:.2f}% | Recall: {recall:.2f}% | F1: {f1:.2f}%")
    print("-" * 40)
    print(f"   TP(침해→침해): {tp} | TN(비침해→비침해): {tn}")
    print(f"   FP(비침해→침해): {fp} | FN(침해→비침해): {fn}")
    print("=" * 60)
    print(f"\n✅ [DONE] 리포트 저장 완료: {output_path}")

if __name__ == '__main__':
    run_evaluation()