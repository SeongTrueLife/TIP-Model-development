"""
scorer.py - Phonetic Similarity Analyzer v5.6.1
==============================================
Update: Advanced Phonetic Weighting & IndexError Protection
Logic: 3-Tier Decision System (Microscope, Telescope, Inclusion)
"""

from rapidfuzz import fuzz, distance
from jamo import h2j, j2hcj

def decompose_text(text):
    """한글 자모 분리 (예: '학' -> 'ㅎㅏㄱ')"""
    if not text: return ""
    try:
        return j2hcj(h2j(text))
    except:
        return text

def calculate_custom_jamo_score(pron_a, pron_b):
    """
    한국어 음운 특성(ㄹ 받침, 까/카 유사성)을 반영한 세밀 유사도 계산
    """
    # h2j를 통한 음절 분해
    j_a = h2j(pron_a)
    j_b = h2j(pron_b)
    
    # 음절 수가 다를 경우 기본 자모 유사도로 전환
    if len(j_a) != len(j_b):
        return fuzz.ratio(j2hcj(j_a), j2hcj(j_b))
    
    total_jamo_score = 0
    total_elements = 0
    
    for char_a, char_b in zip(j_a, j_b):
        # IndexError 방지를 위한 안전장치: 초성+중성 조합 확인
        if len(char_a) < 2 or len(char_b) < 2:
            total_elements += 1
            total_jamo_score += 1.0 if char_a == char_b else 0.0
            continue

        # 음절 분해: [초성, 중성, 종성]
        s_a = [char_a[0], char_a[1], char_a[2] if len(char_a) > 2 else ""]
        s_b = [char_b[0], char_b[1], char_b[2] if len(char_b) > 2 else ""]
        
        for i in range(3):
            total_elements += 1
            val_a, val_b = s_a[i], s_b[i]
            
            if val_a == val_b:
                total_jamo_score += 1.0
            else:
                # 지침 반영: 초성 'ㄲ'과 'ㅋ'의 청감적 유사성 (96%)
                if i == 0 and {val_a, val_b} == {'ㄲ', 'ㅋ'}:
                    total_jamo_score += 0.96
                
                # 지침 반영: 종성 'ㄹ'의 유무 차이 최소화 (98%)
                elif i == 2:
                    if (not val_a and val_b == 'ㄹ') or (val_a == 'ㄹ' and not val_b):
                        total_jamo_score += 0.98
    
    return (total_jamo_score / total_elements) * 100 if total_elements > 0 else 0.0

def calculate_similarity(pron_a, pron_b):
    """ 3-Tier Decision Logic 기반 최종 유사도 산출"""
    if not pron_a or not pron_b:
        return 0.0, "Low", "Error", "데이터 없음"

    a = str(pron_a).replace(" ", "")
    b = str(pron_b).replace(" ", "")
    
    len_a, len_b = len(a), len(b)
    if len_a == 0 or len_b == 0:
        return 0.0, "Low", "N/A", "길이 0"
    
    longer = max(len_a, len_b)
    ratio = min(len_a, len_b) / longer

    # 알고리즘 3대장 점수 산출
    jamo_score = calculate_custom_jamo_score(a, b)
    jw_score = distance.JaroWinkler.similarity(a, b) * 100
    partial_score = fuzz.partial_ratio(a, b)

    final_score = 0.0
    case_name = ""

    # Case 1: Microscope (짧은 단어) -> Jamo 우선
    if longer <= 3 and ratio >= 0.7:
        case_name = "Case 1"
        final_score = (jamo_score * 0.5) + (jw_score * 0.3) + (partial_score * 0.2)

    # Case 2: Telescope (긴 단어) -> JW 우선 (어두 강조)
    elif longer > 3 and ratio >= 0.7:
        case_name = "Case 2"
        final_score = (jw_score * 0.5) + (jamo_score * 0.3) + (partial_score * 0.2)

    # Case 3: Inclusion (길이 차이 큼) -> Partial 우선
    else:
        case_name = "Case 3"
        final_score = (partial_score * 0.7) + (jamo_score * 0.2) + (jw_score * 0.1)

    grade = "High" if final_score >= 80 else "Medium" if final_score >= 50 else "Low"
    return final_score, grade, case_name, ""

def compare(pron_a, pron_b):
    """ 외부 호출용 표준 인터페이스"""
    score, grade, case_name, _ = calculate_similarity(pron_a, pron_b)
    return score, grade, case_name