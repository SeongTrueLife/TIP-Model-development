import json
import csv
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

def calculate_similarity(target_embedding: List[float], 
                        candidate_embeddings: Dict[str, List[float]]) -> List[Tuple[str, float]]:
    """
    타겟 임베딩과 후보 임베딩들을 받아서 유사도 계산 후 정렬된 결과 반환
    
    Args:
        target_embedding: 타겟의 임베딩 벡터 (리스트)
        candidate_embeddings: {파일명: 임베딩벡터} 딕셔너리
    
    Returns:
        [(파일명, 유사도), ...] 리스트 (유사도 내림차순, 소수점 2자리 반올림)
    """
    target_vec = np.array(target_embedding).reshape(1, -1)
    results = []
    
    for name, emb in candidate_embeddings.items():
        can_vec = np.array(emb).reshape(1, -1)
        score = cosine_similarity(target_vec, can_vec)[0][0]
        results.append((name, round(score, 2)))  # 소수점 2자리 반올림
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results

## jsonl 파일에서 데이터 읽어서 타겟/후보 분리
def load_from_jsonl(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    data.jsonl에서 데이터 읽어서 타겟/후보 분리
    
    Returns:
        (targets 리스트, candidates 리스트)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # 중복 제거 (파일 이름 기준)
    unique_data = {}
    for line in lines:
        item = json.loads(line)
        unique_data[item['file_name']] = item
    
    all_items = list(unique_data.values())
    
    # Target과 Candidates 분리
    targets = [d for d in all_items if "_t." in d['file_name'].lower() or "target" in d['file_name'].lower()]
    candidates = [d for d in all_items if "_t." not in d['file_name'].lower() and "target" not in d['file_name'].lower()]
    
    return targets, candidates


def analyze_similarity(jsonl_file: str) -> Dict[str, List[Tuple[str, float]]]:
    """
    JSONL 파일에서 타겟을 로드하고 유사도 분석 수행
    
    Args:
        jsonl_file: data.jsonl 파일 경로
        
    Returns:
        {타겟이름: [(후보명, 유사도), ...]} 딕셔너리
    """
    targets, candidates = load_from_jsonl(jsonl_file)
    
    if not targets:
        print("오류: 'TARGET'가 포함된 file_name을 찾지 못했습니다.")
        print(f"\n현재 {jsonl_file}에 있는 file_name 목록 (처음 10개):")
        with open(jsonl_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10]):
                item = json.loads(line)
                print(f"  {i+1}. {item['file_name']}")
        if len(lines) > 10:
            print(f"  ... 외 {len(lines)-10}개 더 있음")
        print("\n참고: 타겟 상표의 file_name에 'TARGET' 문자열이 포함되어 있어야 합니다.")
        print("예: 'TARGET_logo.jpg' 또는 'logo_TARGET.jpg'")
        return {}
    
    results = {}
    for target in targets:
        target_name = target['file_name']
        # 후보들을 딕셔너리로 변환 {파일명: 임베딩}
        candidate_dict = {c['file_name']: c['embedding'] for c in candidates}
        # 유사도 계산
        similarities = calculate_similarity(target['embedding'], candidate_dict)
        results[target_name] = similarities
    
    return results


# 현재 실행부 (콘솔 출력만)
if __name__ == "__main__":
    analysis_results = analyze_similarity("data.jsonl")
    
    for target_name, similarities in analysis_results.items():
        print(f"\n{'='*60}")
        print(f"기준 상표: {target_name}")
        print(f"{'='*60}")
        print(f"보호상표 | 유사상표 | 유사도")
        print(f"{'-'*60}")
        for name, score in similarities:
            print(f"{target_name} | {name} | {score:.2f}")
        print(f"{'='*60}")
        print(f"총 {len(similarities)}건 처리 완료\n")
