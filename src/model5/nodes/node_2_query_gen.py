"""
[Node 2] Query Generator (Search Planner)

Role:
    RAG 검색(Node 3) 효율을 극대화하기 위해, 상표 정보를 
    '특허청 거절이유서 문체'와 유사한 문장형 쿼리로 변환합니다.

Type:
    LLM (Azure OpenAI GPT-4o-mini)

Output:
    JSON Format: {"queries": ["query1", ...], "keywords": ["keyword1", ...]}
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI

from ..state import AgentState

# 환경 변수 로드 (src/model5/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- [Configuration] ---
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_QUERY", "gpt-4o-mini") # 속도/비용 최적화 모델
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
TEMPERATURE = 0.3 # 약간의 다양성 허용

# --- [System Prompt] ---
SYSTEM_PROMPT = """
**Role**: 
당신은 특허청 상표 심사 데이터베이스(Vector DB) 검색을 위한 **'검색 쿼리 생성 전문가'**입니다.

**Objective**: 
입력된 상표(Trademark) 정보를 분석하여, 특허청 심사관이 작성한 **거절이유서(Rejection Text)의 문체와 가장 유사한 검색 쿼리**를 생성하십시오.
벡터 검색(Vector Similarity Search)의 정확도를 높이기 위해, 키워드 나열보다는 **'법률적 문장(Legal Sentences)'** 형태가 효과적입니다.

**Guidelines**:
1. **Visual Query (외관)**: 
   - `Visual Description`을 참고하여, 도형의 기하학적 형태나 결합 방식을 묘사하는 문장을 만드십시오.
   - 예시: "원이 중첩된 기하학적 도형 내부에 영문자가 결합된 표장", "동물의 형상을 단순화한 로고 타입"

2. **Semantic Query (관념/호칭)**: 
   - `Semantic Description`과 `Product`를 참고하여, 해당 상품에서 흔히 발생하는 식별력 부족 사유(성질표시, 보통명칭 등)를 가정하십시오.
   - 예시: "지정상품 '우유'와 관련하여 '맛있는'은 품질을 직감하게 하므로 식별력이 없음" 

3. **Tone & Style**:
   - 구어체(~해요)를 피하고, **건조하고 딱딱한 법률 문체(~함, ~임, ~으로 판단됨)**를 사용하십시오.

4. **Keywords Extraction**:
   - 검색 필터링에 사용할 핵심 단어(상품명, 핵심 도형 명칭 등)를 별도로 추출하십시오.

**Output Format (JSON Only)**:
반드시 아래 JSON 포맷으로만 응답하십시오. (Markdown 코드블록 없이 순수 JSON)
{
    "queries": [
        "법률적 문체로 작성된 쿼리 문장 1",
        "법률적 문체로 작성된 쿼리 문장 2",
        "법률적 문체로 작성된 쿼리 문장 3"
    ],
    "keywords": ["핵심키워드1", "핵심키워드2", "지정상품명"]
}
"""
#긍정례도 예시추가. 나중에 작업해야됨. 예를들어 2. 관념 호칭 이라든가.

def node_2_query_gen(state: AgentState) -> Dict[str, Any]:
    """
    LLM을 호출하여 RAG 검색용 쿼리와 키워드를 생성합니다.
    """
    
    # 1. 입력 데이터 준비
    target_text = state.get("target_text", "")
    target_product = state.get("target_product", "")
    vis_desc = state.get("vis_desc", "정보 없음")
    sem_desc = state.get("sem_desc", "정보 없음")
    
    user_content = f"""
    [Input Data]
    - Trademark Name: {target_text}
    - Product Categories: {target_product}
    - Visual Description (Node 1 Output): {vis_desc}
    - Semantic Description (Model 4 Output): {sem_desc}
    
    Based on the above, generate optimized search queries in JSON format.
    """

    # 2. Azure Chat Model 초기화
    try:
        llm = AzureChatOpenAI(
            azure_deployment=DEPLOYMENT_NAME,
            openai_api_version=API_VERSION,
            temperature=TEMPERATURE,
            model_kwargs={"response_format": {"type": "json_object"}} # JSON 강제 모드
        )
    except Exception as e:
        # LLM 초기화 실패 시 즉시 Fallback
        return _generate_fallback(target_text, target_product)

    # 3. 메시지 구성
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content)
    ]

    # 4. LLM 실행 및 파싱 (Robust Handling)
    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Markdown Code Block 제거 (방어 로직)
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
            
        # JSON 파싱
        parsed_json = json.loads(content)
        queries = parsed_json.get("queries", [])
        keywords = parsed_json.get("keywords", [])
        
        # 만약 쿼리가 비어있다면 에러로 간주하여 Fallback 유도
        if not queries:
            raise ValueError("Empty queries returned from LLM")
            
        return {
            "rag_queries": {
                "queries": queries,
                "keywords": keywords
            }
        }

    except Exception as e:
        # Fallback: 에러 발생 시 원본 상표명과 상품명을 검색어로 사용
        print(f"[Node 2 Error] JSON Parsing Failed: {e}. Using fallback queries.")
        return _generate_fallback(target_text, target_product)

def _generate_fallback(text: str, product: str) -> Dict[str, Any]:
    """
    에러 발생 시 사용할 기본 쿼리 생성 함수
    """
    fallback_queries = [
        text,
        f"{text} {product}",
        f"{product} 상표 거절 사례"
    ]
    # 빈 문자열 제거 및 유효성 검사
    fallback_queries = [q for q in fallback_queries if q.strip()]
    
    return {
        "rag_queries": {
            "queries": fallback_queries,
            "keywords": [text, product]
        }
    }
