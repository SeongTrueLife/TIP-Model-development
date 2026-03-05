"""
Batch Inference Pipeline for Trademark Analysis (Full Version)
==============================================================
CSV 데이터셋을 읽어와 4개 모델(Visual, Phonetic, Semantic, Judge)을 순차적으로 실행하고,
그 결과를 'baseline_result.csv'에 저장합니다.

[Update]
- Model 4 (Semantic) API 호출 활성화
- RAG (Node 3) 자동 실행 (LangGraph Flow 따름)
- API 비용 및 실행 시간 증가 주의

Usage:
    python -m src.model5.pipeline.run_batch_inference --limit 3  (3건만 테스트)
    python -m src.model5.pipeline.run_batch_inference --all      (전체 데이터 실행)
"""

import os
import sys
import csv
import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# --- [Path Setup] ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Model 5 Graph Import
from src.model5.graph import app
from src.model5.state import AgentState

# Wrapper Import
try:
    from src.model5.pipeline.model_wrapper import (
        VisualModelWrapper, 
        PhoneticModelWrapper, 
        SemanticModelWrapper
    )
except ImportError:
    sys.path.append(str(PROJECT_ROOT / "src" / "model5" / "pipeline"))
    from model_wrapper import VisualModelWrapper, PhoneticModelWrapper, SemanticModelWrapper


# --- [Configuration] ---
DATASET_PATH = PROJECT_ROOT / "src" / "model5" / "dataset" / "judicial_precedent_dataset" / "trademark_dataset_mixed.csv"
IMAGE_DIR = PROJECT_ROOT / "src" / "model5" / "dataset" / "judicial_precedent_dataset" / "image"
OUTPUT_DIR = PROJECT_ROOT / "src" / "model5" / "dataset"
OUTPUT_FILE = OUTPUT_DIR / f"baseline_result_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"


def run_pipeline(limit: int = 0, target_split: str = "test"):
    print(f"\n[Pipeline Start] Loading dataset from {DATASET_PATH}...")
    
    if not DATASET_PATH.exists():
        print(f"[Error] Dataset file not found: {DATASET_PATH}")
        return

    df = pd.read_csv(DATASET_PATH)
    
    # Filter by split
    if target_split and 'split' in df.columns:
        original_len = len(df)
        df = df[df['split'] == target_split]
        print(f"[Info] Filtered by split='{target_split}': {original_len} -> {len(df)} rows")
    elif target_split:
        print(f"[Warning] 'split' column not found in dataset. Ignoring filter '{target_split}'.")
    
    if limit > 0:
        df = df.head(limit)
        print(f"[Info] Running on first {limit} rows only.")
    
    print("\n[Init] Initializing Models...")
    try:
        vis_model = VisualModelWrapper()
        pho_model = PhoneticModelWrapper()
        sem_model = SemanticModelWrapper()
        print("[Success] All models loaded.")
    except Exception as e:
        print(f"[Critical Error] Failed to load models: {e}")
        return

    results = []
    
    print(f"\n[Processing] Start batch inference on {len(df)} items...")
    print("[Warning] API calls enabled. This may take time and cost money.\n")
    
    # tqdm으로 진행 상황 표시
    pbar = tqdm(total=len(df), desc="Analyzing")
    
    for idx, row in df.iterrows():
        case_id = row.get('case_id', f'unknown_{idx}')
        
        target_text = str(row.get('target_text', ''))
        cited_text = str(row.get('cited_text', ''))
        
        target_img_name = str(row.get('target_img', ''))
        cited_img_name = str(row.get('cited_img', ''))
        
        target_img_path = IMAGE_DIR / target_img_name
        cited_img_path = IMAGE_DIR / cited_img_name
        
        # 이미지 확인
        if not target_img_path.exists():
             # 파일 없으면 건너뛰기
            pbar.update(1)
            continue
            
        # --- [Step 2: Model Execution (Raw Scores)] ---
        # 1. Visual Score (Model 2)
        try:
            # cited_img가 없으면 0점 처리 (비교 대상 없음)
            if cited_img_path.exists():
                raw_vis = vis_model.get_score(str(target_img_path), str(cited_img_path))
            else:
                raw_vis = 0.0
        except Exception as e:
            # print(f"[Vis Error] {e}")
            raw_vis = 0.0
            
        # 2. Phonetic Score (Model 3)
        try:
            raw_pho, pho_trans = pho_model.get_score(target_text, cited_text)
        except Exception as e:
            # print(f"[Pho Error] {e}")
            raw_pho, pho_trans = 0.0, ""
            
        # 3. Semantic Score (Model 4) - API Active!
        try:
            if cited_img_path.exists():
                raw_sem, sem_desc = sem_model.get_score(str(target_img_path), str(cited_img_path))
            else:
                raw_sem, sem_desc = 0.0, ""
        except Exception as e:
            # print(f"[Sem Error] {e}")
            raw_sem, sem_desc = 0.0, ""
            
        # --- [Step 3: Model 5 Execution (Integration)] ---
        # 이미지 데이터 로드 (Base64)
        import base64
        try:
            with open(target_img_path, "rb") as img_file:
                target_img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
        except:
            target_img_b64 = ""

        initial_state = {
            "base_scores": {
                "visual": raw_vis,
                "phonetic": raw_pho,
                "semantic": raw_sem
            },
            "target_text": target_text,
            "target_product": str(row.get('target_prod', '')),
            "target_img": target_img_b64, 
            "sem_desc": sem_desc, # [Model 4 Output] 관념 묘사 전달
            # rag_contexts는 비워두면 Node 3가 실행되어 채워짐 (Graph Flow)
        }
        
        try:
            final_state = app.invoke(initial_state)
            
            cal_scores = final_state.get('calibrated_scores', {})
            final_res = final_state.get('final_score', 0.0)
            risk = final_state.get('risk_level', 'Unknown')
            report = final_state.get('report_meta', {})
            
            # --- [Step 4: Record Results] ---
            result_row = row.to_dict()
            
            result_row['raw_vis'] = raw_vis
            result_row['raw_pho'] = raw_pho
            result_row['raw_sem'] = raw_sem
            
            result_row['cal_vis'] = cal_scores.get('visual', 0.0)
            result_row['cal_pho'] = cal_scores.get('phonetic', 0.0)
            result_row['cal_sem'] = cal_scores.get('semantic', 0.0)
            
            # [Added] Dynamic Weights (Node 5 Result)
            weights = final_state.get('dynamic_weights', {})
            result_row['weight_vis'] = weights.get('visual', 0.0)
            result_row['weight_pho'] = weights.get('phonetic', 0.0)
            result_row['weight_sem'] = weights.get('semantic', 0.0)
            
            # [Added] Legal Grade (Node 4 Result)
            legal = final_state.get('legal_analysis', {})
            result_row['grade_vis'] = legal.get('visual', {}).get('grade_score', 0)
            result_row['grade_pho'] = legal.get('phonetic', {}).get('grade_score', 0)
            result_row['grade_sem'] = legal.get('semantic', {}).get('grade_score', 0)
            
            # [Added] Descriptions & Reasons
            result_row['vis_desc'] = final_state.get('vis_desc', '')
            result_row['sem_desc'] = final_state.get('sem_desc', '')
            result_row['pho_trans'] = pho_trans  # [Model 3 Output] 발음 변환 결과
            
            result_row['reason_vis'] = legal.get('visual', {}).get('reason', '')
            result_row['reason_pho'] = legal.get('phonetic', {}).get('reason', '')
            result_row['reason_sem'] = legal.get('semantic', {}).get('reason', '')
            
            result_row['final_score'] = final_res
            result_row['risk_level'] = risk
            result_row['logic_type'] = report.get('logic_type', 'N/A')
            result_row['judge_reason'] = report.get('message', '')
            
            # RAG 결과도 궁금하면 저장 (옵션)
            # result_row['rag_count'] = len(final_state.get('rag_contexts', []))
            
            results.append(result_row)
            
        except Exception as e:
            print(f"[Error] Model 5 Failed on {case_id}: {e}")
            pass
            
        pbar.update(1)
        
    pbar.close()

    if results:
        df_result = pd.DataFrame(results)
        
        # --- [Column Reordering] ---
        # 분석하기 편한 순서로 컬럼 재배열
        desired_order = [
            # 1. Basic Info
            'case_id', 'split', 'target_text', 'target_img', 'target_prod', 
            'p_trademark_class_code', 'cited_text', 'cited_img', 'cited_prod', 
            'c_trademark_class_code', 'result', 'main_factor', 'sim_level', 'note',
            
            # 2. Visual Group
            'raw_vis', 'cal_vis', 'grade_vis', 'weight_vis', 'vis_desc', 'reason_vis',
            
            # 3. Phonetic Group
            'raw_pho', 'cal_pho', 'grade_pho', 'weight_pho', 'pho_trans', 'reason_pho',
            
            # 4. Semantic Group
            'raw_sem', 'cal_sem', 'grade_sem', 'weight_sem', 'sem_desc', 'reason_sem',
            
            # 5. Final Result
            'final_score', 'risk_level', 'logic_type', 'judge_reason'
        ]
        
        # 실제 데이터프레임에 존재하는 컬럼만 선택하고, 정의되지 않은 나머지 컬럼은 뒤에 붙임
        existing_cols = df_result.columns.tolist()
        final_order = [c for c in desired_order if c in existing_cols] + \
                      [c for c in existing_cols if c not in desired_order]
        
        df_result = df_result[final_order]
        
        df_result.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"\n[Done] Saved {len(df_result)} results to {OUTPUT_FILE}")
    else:
        print("\n[Warning] No results to save.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3, help="Number of rows to test (default: 3)")
    parser.add_argument("--all", action="store_true", help="Run on all data")
    parser.add_argument("--split", type=str, default="test", help="Filter by split column (default: 'test')")
    
    args = parser.parse_args()
    
    limit_cnt = args.limit
    if args.all:
        limit_cnt = 0
        
    run_pipeline(limit=limit_cnt, target_split=args.split)
