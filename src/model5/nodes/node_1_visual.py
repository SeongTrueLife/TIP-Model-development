"""
[Node 1] Visual Describer (Agent A)

Role:
    Vision LLM을 사용하여 상표 이미지를 '객관적인 텍스트'로 상세 묘사합니다.
    이 묘사는 이후 검색(Query Generation)과 법적 판단(Legal Judge)의 기초 자료로 활용됩니다.

Type:
    LLM (Azure OpenAI GPT-4o / GPT-4-Turbo Vision)

Note:
    실제 모델명은 Azure 배포 설정에 따라 다를 수 있으므로 환경변수나 상수로 관리합니다.
"""

import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# LangChain Imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

from ..state import AgentState

# 환경 변수 로드 (src/model5/.env)
# 현재 파일: src/model5/nodes/node_1_visual.py -> parent.parent가 src/model5
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- [Configuration] ---
# Azure OpenAI 설정 (환경변수가 없으면 코드 내 기본값 사용 - 주의 필요)
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_VISUAL", "gpt-5.1-chat")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
# TEMPERATURE = 0.0  # 사실적 묘사를 위해 창의성 최소화, azure의 gpt-5.1-chat은 temperature 설정이 불가능한것으로 보임.

# --- [System Prompt] ---
SYSTEM_PROMPT = """
**Role**: 
당신은 대한민국 특허청(KIPO) 소속의 20년 경력 베테랑 상표 디자인 심사관입니다.
당신의 임무는 주어진 상표 이미지를 보지 못하는 동료 심사관을 위해, 이미지를 **글로 완벽하게 복원할 수 있을 정도로 상세하고 객관적이며 구조적으로 묘사**하는 것입니다.

**Task**: 
주어진 상표 이미지를 분석하여 다음 3가지 관점에서 상세히 서술하십시오.

**Guidelines**:
1. **객관성 유지 (Objectivity)**:
   - "예쁘다", "세련되다", "강렬하다" 등의 주관적/추상적 형용사는 절대 사용하지 마십시오.
   - 대신 "채도가 높은 적색", "굵기 2mm의 직선", "우측 상단에 배치된" 등 **물리적 특징**을 서술하십시오.

2. **구조적 분해 (Structured Analysis)**:
   - **[도형적 요소]**: 기하학적 형상(원, 사각형 등), 묘사된 사물(사자, 나무 등)의 구체적 생김새, 라인의 형태(실선, 점선).
   - **[문자적 요소]**: 이미지 내에 포함된 모든 텍스트, 폰트 스타일(고딕, 명조, 필기체 등), 텍스트의 배치(도형의 내부/하단 등).
   - **[색상 및 구성]**: 주요 색상 코드(가능하다면) 또는 색상 명칭, 배경색과 전경색의 대비.

3. **출력 형식 (Output Format)**:
   - 서술형 줄글(Paragraph)로 작성하되, 위 3가지 요소를 자연스럽게 포함하십시오.
   - 반드시 **한국어(Korean)**로 작성하십시오.

**Warning**:
이 단계에서는 해당 상표의 등록 가능성이나 침해 여부를 절대 판단하지 마십시오. 오직 **'보이는 사실(Visual Facts)'**만 전달해야 합니다.
"""

def node_1_visual(state: AgentState) -> Dict[str, Any]:
    """
    Vision LLM을 호출하여 target_img에 대한 vis_desc를 생성합니다.
    """
    
    # 1. 입력 데이터 준비 및 검증
    raw_image_data = state.get("target_img")
    
    if not raw_image_data:
        return {"vis_desc": "이미지 데이터가 제공되지 않았습니다."}

    # 2. 이미지 포맷 핸들링 (Robust Handling)
    # URL인지, Base64인지, 헤더가 있는지 없는지 판별
    final_image_url = ""
    
    # URL Case
    if raw_image_data.startswith("http://") or raw_image_data.startswith("https://"):
        final_image_url = raw_image_data
        
    # Base64 with Header Case (e.g., data:image/png;base64,...)
    elif raw_image_data.startswith("data:image"):
        final_image_url = raw_image_data
        
    # Raw Base64 String Case
    else:
        # Default to jpeg if no header provided
        final_image_url = f"data:image/jpeg;base64,{raw_image_data}"

    # 3. Azure Chat Model 초기화
    try:
        llm = AzureChatOpenAI(
            azure_deployment=DEPLOYMENT_NAME,
            openai_api_version=API_VERSION,
            #temperature=TEMPERATURE,
            max_tokens=1000, 
        )
    except Exception as e:
        return {"vis_desc": f"LLM 초기화 실패: {str(e)}"}

    # 4. 메시지 구성
    # System Message: 페르소나 부여
    # Human Message: 이미지 + 지시어
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": "이 상표 이미지를 가이드라인에 맞춰 상세히 묘사해줘."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": final_image_url},
                    "detail": "high", #문제가 될 시 이부분 삭제.
                },
            ]
        )
    ]

    # 5. LLM 실행 및 예외 처리
    try:
        response = llm.invoke(messages)
        description = response.content
    except Exception as e:
        # API 호출 실패 시, 파이프라인이 멈추지 않도록 에러 메시지 반환
        description = f"시각적 묘사 생성 실패 (API Error): {str(e)}"

    # 6. 결과 반환 (State Update)
    return {
        "vis_desc": description
    }
