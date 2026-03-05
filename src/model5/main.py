"""
[Model 5] Execution Runner (Entry Point)

Role:
    Model 5 파이프라인을 실행하고 테스트하는 메인 스크립트입니다.
    두 가지 모드를 지원합니다:
    1. --mode logic: LLM API 호출 없이 수학적 계산 로직(N0, N5, N6)만 검증 (비용 0원)
    2. --mode full: 실제 LangGraph를 구동하여 전체 파이프라인 실행

Usage:
    python -m src.model5.main --mode logic
    python -m src.model5.main --mode full
"""

import os
import argparse
import json
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv

# 환경 변수 로드 (src/model5/.env)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
from src.model5.graph import app
from src.model5.state import AgentState

# Individual Nodes Import (for Logic Test)
from src.model5.nodes.node_0_calibrator import score_calibrator
from src.model5.nodes.node_5_weight_mapper import weight_mapper
from src.model5.nodes.node_6_calculator import final_calculator

# 환경 변수 로드
load_dotenv()

# --- [Test Data Configuration] ---
# 테스트용 로컬 이미지 경로 (User Provided)
SAMPLE_IMG_PATH = r"src/model5/test_img/removed_bg_5.png"

def run_logic_test():
    """
    [Mode: Logic Test]
    LLM 호출 없이 순수 파이썬 로직(Calibrator -> WeightMapper -> Calculator)만 단위 테스트합니다.
    """
    print("\n[Mode: Logic Test] Starting verification without LLM calls...")
    
    # 1. Mock Input (Raw Scores & Basic Info)
    # 가정: BRKA (Safe Case)
    mock_state = {
        "base_scores": {'visual': 0.25, 'phonetic': 0.30, 'semantic': 0.10},
        "target_text": "BRKA",
        "target_product": "샴푸, 헤어 케어 제품",
        # 나머지 필드는 초기화 시 없어도 됨 (Dict access)
    }
    
    print("\n1. [Input] Base Scores:", mock_state['base_scores'])

    # 2. Node 0 실행 (Score Calibrator)
    print("\n>>> Running Node 0 (Calibrator)...")
    update0 = score_calibrator(mock_state)
    mock_state.update(update0)
    print(f"   -> Calibrated Scores: {mock_state['calibrated_scores']}")

    # 3. Mock Node 4 Output (Legal Judge)
    # LLM이 할 일을 가짜 데이터로 대체
    print("\n>>> Mocking Node 4 (Judge)...")
    mock_legal_analysis = {
        "visual": {
            "grade_score": 5, 
            "grade_label": "Grade 5 (Exclusive)", 
            "reason": "Mock Reason: Highly unique geometric combination."
        },
        "phonetic": {
            "grade_score": 3, 
            "grade_label": "Grade 3 (Moderate)", 
            "reason": "Mock Reason: Suggestive term."
        },
        "semantic": {
            "grade_score": 2, 
            "grade_label": "Grade 2 (Weak)", 
            "reason": "Mock Reason: Slightly descriptive."
        }
    }
    mock_state['legal_analysis'] = mock_legal_analysis
    print("   -> Mocked Judge Output Applied.")

    # 4. Node 5 실행 (Weight Mapper)
    print("\n>>> Running Node 5 (Weight Mapper)...")
    update5 = weight_mapper(mock_state)
    mock_state.update(update5)
    print(f"   -> Dynamic Weights: {mock_state['dynamic_weights']}")

    # 5. Node 6 실행 (Final Calculator)
    print("\n>>> Running Node 6 (Final Calculator)...")
    result = final_calculator(mock_state)
    
    # 결과 출력
    print("\n" + "="*40)
    print(f"FINAL SCORE : {result['final_score']}")
    print(f"RISK LEVEL  : {result['risk_level']}")
    print("-" * 40)
    print("[Report Meta]")
    pprint(result['report_meta'])
    print("="*40 + "\n")


def run_full_pipeline():
    """
    [Mode: Full Pipeline]
    실제 LangGraph를 구동하여 Start부터 End까지 전체 과정을 실행합니다.
    Azure OpenAI API 호출이 발생하므로 비용이 청구됩니다.
    """
    print("\n[Mode: Full Pipeline] Starting full workflow execution (API Calls will occur)...")
    
    # 1. 이미지 로드 (Base64 Encoding)
    # 로컬 파일을 읽어서 Base64 문자열로 변환하거나 URL을 사용
    target_img_data = SAMPLE_IMG_PATH
    
    # 파일이 실제로 존재하면 Base64로 읽기 시도, 아니면 경로 문자열 그대로 사용 (Node 1이 처리)
    if os.path.exists(SAMPLE_IMG_PATH):
        import base64
        try:
            with open(SAMPLE_IMG_PATH, "rb") as img_file:
                # Node 1에서 data:image 헤더를 붙여주므로 여기서는 raw bytes만 인코딩
                b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                target_img_data = b64_str
            print(f"   -> Image loaded from local path (Length: {len(target_img_data)})")
        except Exception as e:
            print(f"   -> Warning: Failed to read image file. Using path string. Error: {e}")
    else:
        print(f"   -> Warning: Image file not found at {SAMPLE_IMG_PATH}. Using path string.")

    # 2. 초기 상태 설정 (Initial State)
    initial_inputs = {
        "target_img": target_img_data,
        "target_text": "BRKA",
        "target_product": "샴푸, 헤어 케어 제품",
        "base_scores": {'visual': 0.25, 'phonetic': 0.30, 'semantic': 0.10}, # (비슷한게 거의 없음 -> Safe 예상)
        "sem_desc": "검은색의 굵은 영문 알파벳이 세로로 배열된 단순하고 모던한 도안"
    }
    
    print(f"   -> Target: {initial_inputs['target_text']} (Product: {initial_inputs['target_product']})")
    
    # 3. 그래프 실행 (Invoke)
    print("\n>>> Invoking LangGraph App...")
    try:
        # stream 대신 invoke 사용 (동기 실행)
        final_state = app.invoke(initial_inputs)
        
        # 4. 결과 출력
        print("\n" + "="*40)
        print(">>> [FINAL EXECUTION RESULT]")
        print(f"Final Score : {final_state.get('final_score')}")
        print(f"Risk Level  : {final_state.get('risk_level')}")
        print("-" * 40)
        
        print("\n[1. Visual Description]")
        print(final_state.get('vis_desc')[:200] + "...") # 너무 기니까 앞부분만
        
        print("\n[2. RAG Queries]")
        pprint(final_state.get('rag_queries'))
        
        print(f"\n[3. Retrieved Contexts] ({len(final_state.get('rag_contexts', []))} cases)")
        
        print("\n[4. Legal Analysis (Judge)]")
        pprint(final_state.get('legal_analysis'))
        
        print("\n[5. Calculation Logic]")
        pprint(final_state.get('report_meta'))
        print("="*40 + "\n")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model 5 Pipeline Runner")
    parser.add_argument("--mode", type=str, default="logic", choices=["logic", "full"], 
                        help="Select execution mode: 'logic' (no LLM) or 'full' (real pipeline)")
    
    args = parser.parse_args()
    
    if args.mode == "logic":
        run_logic_test()
    else:
        run_full_pipeline()
