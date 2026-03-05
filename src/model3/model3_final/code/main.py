"""
main.py - Phonetic Similarity Analyzer v5.6.2
=============================================
Update: 
1. Duplicate Update Logic (Excel Optimization)
2. Fragment Filtering (Preventing "GS" vs "GS" fake match)
"""

import os
import pandas as pd
from datetime import datetime
import converter
import scorer
import re

# 1. 경로 설정 및 파일 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "analysis_log.xlsx")

def save_to_excel(result_data):
    """
    결과를 엑셀에 저장하되, 동일한 상표 쌍(대소문자 무관)은 
    기존 기록을 삭제하고 최신 결과로 업데이트합니다.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_excel(LOG_FILE)
        except:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    new_row = pd.DataFrame([result_data])

    if not df.empty:
        df['temp_match'] = df['brand_a'].str.lower() + "_" + df['brand_b'].str.lower()
        target_match = result_data['brand_a'].lower() + "_" + result_data['brand_b'].lower()
        
        df = df[df['temp_match'] != target_match].copy()
        df = df.drop(columns=['temp_match'])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(LOG_FILE, index=False)

def detect_input_type(text):
    if re.match(r'^[가-힣\s]+$', text): return "한글"
    if re.match(r'^[a-zA-Z\s]+$', text): return "영문"
    if re.search(r'[0-9]', text): return "숫자/기호 포함"
    return "혼합(한글+영문)"

def get_case_description(case_name):
    descriptions = {
        "Case 1": "Microscope (짧은 상표) → 자모(Jamo) 50% + JW 30% + Partial 20%",
        "Case 2": "Telescope (긴 상표) → JW 50% + 자모(Jamo) 30% + Partial 20%",
        "Case 3": "Inclusion (길이 차이 큼) → Partial 70% + 자모(Jamo) 20% + JW 10%",
    }
    return descriptions.get(case_name, case_name)

def run_analysis():
    print("\n" + "="*60)
    print("Phonetic Similarity Analyzer v5.6.2 (Final Integration)")
    print("="*60)

    brand_a = input("\n상표 A 입력 (종료: q): ").strip()
    if brand_a.lower() == 'q': return
    brand_b = input("상표 B 입력: ").strip()

    type_a = detect_input_type(brand_a)
    type_b = detect_input_type(brand_b)

    print("\n" + "-"*50)
    print("📌 [Step 1] 입력 분석")
    print(f"   상표 A: '{brand_a}' ({type_a})")
    print(f"   상표 B: '{brand_b}' ({type_b})")

    # 1. 발음 변환 (복수 후보군)
    pair = converter.convert_pair(brand_a, brand_b)
    list_a = pair['korean_a']
    list_b = pair['korean_b']
    
    print("\n📌 [Step 2] 발음 변환 (GPT + 연음법칙 적용)")
    print(f"   '{brand_a}' → {list_a}")
    print(f"   '{brand_b}' → {list_b}")

    # ✅ [핵심 추가] 파편 발음 필터링 (Fragment Filter)
    # 가장 긴 발음의 80% 이상 길이만 유효한 비교 대상으로 삼음 (지에스 vs 지에스이시보 방지)
    max_len_a = max(len(p) for p in list_a)
    max_len_b = max(len(p) for p in list_b)
    valid_a = [p for p in list_a if len(p) >= max_len_a * 0.8]
    valid_b = [p for p in list_b if len(p) >= max_len_b * 0.8]

    # 2. 교차 검증
    best = {"score": -1.0, "p_a": "", "p_b": "", "case": "", "grade": ""}
    all_combos = []
    
    for p_a in valid_a:
        for p_b in valid_b:
            score, grade, case = scorer.compare(p_a, p_b)
            all_combos.append((p_a, p_b, score, case))
            if score > best["score"]:
                best.update({
                    "score": score, "p_a": p_a, "p_b": p_b, 
                    "case": case, "grade": grade
                })

    print(f"\n📌 [Step 3] 유사도 점수화")
    print(f"   적용 로직: {best['case']} - {get_case_description(best['case'])}")
    
    if len(all_combos) > 1:
        print(f"   교차 검증 결과:")
        for p_a, p_b, sc, cs in all_combos:
            marker = " ◀ 최고점" if sc == best["score"] else ""
            print(f"     {p_a} vs {p_b} → {sc:.2f}점 ({cs}){marker}")
    else:
        print(f"   대표 발음: {best['p_a']} vs {best['p_b']}")
        print(f"   유사도 점수: {best['score']:.2f}점")

    # 3. 최종 판정
    final_decision = "침해(유사)" if best["score"] >= 80 else "비침해(비유사)"
    
    result_res = {
        "brand_a": brand_a, "brand_b": brand_b,
        "best_match_a": best["p_a"], "best_match_b": best["p_b"],
        "max_score": round(best["score"], 2), "decision": final_decision,
        "logic_case": best["case"],
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_to_excel(result_res)

    print(f"\n{'='*50}")
    print(f"🏛️ [최종 판정]")
    print(f"   {best['p_a']} vs {best['p_b']} → {best['score']:.2f}점")
    print(f"   본 모델은 해당 건을 [{final_decision}]로 판단합니다.")
    print(f"{'='*50}")
    print(f"📊 결과가 {LOG_FILE}에 저장되었습니다.")

if __name__ == "__main__":
    while True:
        run_analysis()