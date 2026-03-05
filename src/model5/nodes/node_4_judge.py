"""
[Node 4] Legal Judge (Agent B)

Role:
    판례(RAG Context)와 상표 정보를 종합하여 식별력 등급(Grade 1~5)을 판정합니다.
    이 판단 결과는 Node 5(Weight Mapper)에서 수치 가중치로 변환됩니다.

Type:
    LLM (Azure OpenAI GPT-5.1-chat / GPT-4o)

Output:
    JSON Format:
    {
        "visual": {"grade_score": int, "grade_label": str, "reason": str},
        "phonetic": { ... },
        "semantic": { ... }
    }
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI

from ..state import AgentState

# 환경 변수 로드 (src/model5/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- [Configuration] ---
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_JUDGE", "gpt-5.1-chat")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
# TEMPERATURE = 0.0 # 법적 판단의 일관성을 위해 0으로 설정, azure의 gpt-5.1-chat은 temperature 설정이 불가능한것으로 보임.

# --- [System Prompt] ---
SYSTEM_PROMPT = """
**Role**: 
당신은 대한민국 특허청(KIPO)의 수석 상표 심사관입니다. 20년 이상의 심사 경력을 바탕으로, 상표의 식별력(Distinctiveness)을 엄격하게 평가하십시오.

**Task**: 
제공된 [Target Trademark] 정보와 [Precedents & Guidelines]를 종합 분석하여, Visual(외관), Phonetic(호칭), Semantic(관념) 3가지 측면의 식별력 등급을 판정하십시오.

**Grading System (5-Tier)**:
- **Grade 5 (Exclusive / 독점적)**: 
  - 조어(Coined word), 매우 독창적인 도안. 누구도 사용하지 않는 창작적 표장.
- **Grade 4 (Strong / 강함)**: 
  - 흔하지 않은 단어, 독특한 결합. 암시적이지만 창작성이 높은 경우.
- **Grade 3 (Moderate / 보통)**: 
  - 암시적(Suggestive) 표장. 직감적이진 않으나 어느 정도 사고 과정이 필요함. (Default)
- **Grade 2 (Weak / 약함)**: 
  - 성질표시(Descriptive), 흔한 표장, 간단한 도형, 지리적 명칭. 식별력이 미약함.
- **Grade 1 (None / 없음)**: 
  - 관용표장, 보통명칭(Generic), 식별 불가능한 간단한 문자/도형.

**Requirements**:
1. **Evidence-Based**: 반드시 제공된 `Precedents (유사 판례)`를 인용하여 판단 근거(Reason)를 서술하십시오. 판례가 없다면 일반적인 심사 기준을 따르십시오.
2. **Strict Output Format**: 반드시 아래 JSON 포맷으로만 응답하십시오. (Markdown 코드블록 제외 권장)
 - 'grade_score' 필드는 반드시 숫자(Integer 1~5)여야 합니다. (문자열 금지)

```json
{
  "visual": { 
    "grade_score": 5, 
    "grade_label": "Grade 5 (Exclusive)", 
    "reason": "판례 [Case ID: 12345]에 따르면 기하학적 도형의 결합은 독창성을 인정받아..." 
  },
  "phonetic": { 
    "grade_score": 3, 
    "grade_label": "Grade 3 (Moderate)", 
    "reason": "..." 
  },
  "semantic": { 
    "grade_score": 1, 
    "grade_label": "Grade 1 (None)", 
    "reason": "지정상품 '우유'에 대해 '맛있는'은 성질표시에 해당하므로..." 
  }
}
```
"""

def _get_fallback_result(reason: str) -> Dict[str, Dict[str, Any]]:
    """
    분석 실패 시 사용할 기본값 (Grade 3 - Moderate)
    """
    default_item = {
        "grade_score": 3, 
        "grade_label": "Grade 3 (Moderate)", 
        "reason": reason
    }
    return {
        "visual": default_item,
        "phonetic": default_item,
        "semantic": default_item
    }

def node_4_judge(state: AgentState) -> Dict[str, Any]:
    """
    LLM을 호출하여 법적 판단(식별력 등급)을 수행합니다.
    """
    
    # 1. 입력 데이터 준비
    target_text = state.get("target_text", "")
    target_product = state.get("target_product", "")
    vis_desc = state.get("vis_desc", "N/A")
    sem_desc = state.get("sem_desc", "N/A")
    
    # RAG Contexts (리스트를 하나의 텍스트로 병합)
    rag_contexts_list = state.get("rag_contexts", [])
    if rag_contexts_list:
        rag_text = "\n\n".join(rag_contexts_list)
    else:
        rag_text = "(검색된 유사 판례가 없습니다. 일반적인 심사 기준을 적용하십시오.)"
        
    # Calibrated Scores (참고용 정량 지표)
    scores = state.get("calibrated_scores", {})
    score_summary = (
        f"- Visual Similarity Score: {scores.get('visual', 0):.2f}\n"
        f"- Phonetic Similarity Score: {scores.get('phonetic', 0):.2f}\n"
        f"- Semantic Similarity Score: {scores.get('semantic', 0):.2f}"
    )

    user_content = f"""
    [Target Trademark Information]
    - Text: "{target_text}"
    - Product: "{target_product}"
    - Visual Description: {vis_desc}
    - Semantic Description: {sem_desc}
    
    [Quantitative Analysis (Reference Only)]
    {score_summary}
    
    [Precedents & Guidelines (RAG Context)]
    {rag_text}
    
    Based on the above, analyze the distinctiveness and output JSON.
    """

    # 2. Azure Chat Model 초기화
    try:
        llm = AzureChatOpenAI(
            azure_deployment=DEPLOYMENT_NAME,
            openai_api_version=API_VERSION,
            # temperature=TEMPERATURE,
            model_kwargs={"response_format": {"type": "json_object"}} # JSON 강제
        )
    except Exception as e:
        print(f"[Node 4 Error] LLM Init Failed: {e}")
        return {"legal_analysis": _get_fallback_result(f"System Error: {str(e)}")}

    # 3. 메시지 구성
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]

    # 4. LLM 실행 및 파싱 (Robust Handling)
    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Markdown Cleaning
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
            
        result_json = json.loads(content)
        
        # 필수 키 검증
        required_keys = ["visual", "phonetic", "semantic"]
        if not all(key in result_json for key in required_keys):
            raise ValueError("Missing required keys in LLM output")
            
        return {"legal_analysis": result_json}

    except json.JSONDecodeError:
        print("[Node 4 Error] JSON Parsing Failed. Falling back to default.")
        return {"legal_analysis": _get_fallback_result("JSON Parsing Failed")}
        
    except Exception as e:
        print(f"[Node 4 Error] Analysis Failed: {e}")
        return {"legal_analysis": _get_fallback_result(f"Analysis Error: {str(e)}")}
