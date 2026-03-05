import os
import base64
import json
import time
from typing import List
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from config import (
    AZURE_API_KEY, AZURE_API_VERSION, AZURE_ENDPOINT,
    MODEL_NAME, EMBEDDING_MODEL, TARGET_DIR, CANDIDATE_DIR, 
    OUTPUT_FILE, SLEEP_TIME, validate_config
)

# Azure 설정 검증 및 클라이언트 초기화
validate_config()
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
)

# 2. 이미지 인코딩 함수 (로컬 파일을 GPT로 전달하기 위함)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 3. GPT-5.1을 이용한 관념 분석 함수
def generate_description(image_path):
    base64_image = encode_image(image_path)
    
    system_msg = """당신은 상표법 전문가입니다. 당신의 역할은 두 상표의 유사 여부를 결정하는 것이 아니라, 임베딩 모델이 유사도를 정확히 측정할 수 있도록 상표의 관념적 구성 요소를 객관적이고 풍부하게 묘사하는 것입니다.

특히 다음 원칙을 준수하세요:
- 결론 배제: "유사하다", "상이하다", "독립적이다"와 같은 주관적 판단을 절대 하지 마십시오.
- 요부 추출: 상표에서 식별력이 강한 '핵심 단어(요부)'가 무엇인지 분석하십시오.
- 언어적 확장: 해당 단어가 실생활에서 어떻게 약칭되거나 변형되어 불릴 수 있는지(예: '또또사랑' -> '또또') 가능성을 열어두고 서술하십시오.

[프롬프트 내용] 다음 상표 이미지와 텍스트를 분석하여 상표법적 '관념(Conception)' 묘사문을 작성해줘. 묘사는 반드시 다음 세 가지 요소를 포함해야 해:

- 사전적 정의 (Literal Meaning): 상표에 포함된 텍스트나 핵심 오브젝트가 가진 객관적인 사전적 의미와 동의어를 서술해줘. (예: "THERMAL" -> 열의, 온도의, 뜨거운)
- 시각적 뉘앙스 (Visual Nuance): 로고의 스타일, 색상, 구도가 주는 심상과 분위기를 형용사로 표현해줘. (예: 따뜻한, 권위적인, 현대적인)
- 종합적 관념 (Total Conception): 일반 수요자가 이 상표를 보았을 때 직관적으로 떠올리게 되는 최종적인 '인상'을 요약해줘.

[제약 사항]
- 모든 묘사는 한국어로 통일할 것.
- 법리적 판단의 근거가 될 수 있도록 명확하고 전문적인 용어를 사용할 것.
- 전체 길이는 300자 내외로 작성할 것."""

    try:
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "이 상표 이미지와 텍스트를 분석해 위 지침에 따라 관념을 묘사해줘.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            },
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_completion_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error 분석 중: {e}")
        return None

# 4. 텍스트를 벡터로 변환하는 함수
def get_embedding(text):
    if not text:
        print("임베딩 입력 텍스트가 비어 있습니다. (설명 생성 실패)")
        return None
    try:
        response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error 임베딩 중: {e}")
        return None

# 5. 실행 로직 (1:100 테스트 시나리오)
def run_test():
    # 경로 설정 (config.py에서 로드됨)
    
    # 후보군(100개) 처리 및 저장
    if os.path.exists(CANDIDATE_DIR):
        print("--- 후보군(Candidates) 분석 시작 ---")
        for file_name in os.listdir(CANDIDATE_DIR):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(CANDIDATE_DIR, file_name)
                print(f"분석 중: {file_name}")
                
                desc = generate_description(img_path)
                if desc:
                    vec = get_embedding(desc)
                    result = {
                        "file_name": file_name,
                        "description": desc,
                        "embedding": vec
                    }
                    # JSONL 파일에 저장
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")
                time.sleep(SLEEP_TIME) # Rate Limit 방지

    # 기준 상표(1개) 처리 및 저장
    print("\n--- 기준 상표(Target) 분석 시작 ---")
    if os.path.exists(TARGET_DIR):
        for file_name in os.listdir(TARGET_DIR):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(TARGET_DIR, file_name)
                print(f"분석 중: {file_name}")
                
                desc = generate_description(img_path)
                if desc:
                    vec = get_embedding(desc)
                    if vec:
                        # 파일명 그대로 저장 (파일명에 TARGET이 포함되어 있으면 그대로 사용)
                        result = {
                            "file_name": file_name,  # 원본 파일명 그대로 사용
                            "description": desc,
                            "embedding": vec
                        }
                        # JSONL 파일에 저장
                        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                            f.write(json.dumps(result, ensure_ascii=False) + "\n")
                        print(f"기준 상표[{file_name}] 분석 및 벡터화 완료!")
                    else:
                        print(f"기준 상표[{file_name}] 임베딩 생성 실패")
                else:
                    print(f"기준 상표[{file_name}] 설명 생성 실패, 임베딩 생략")
                time.sleep(SLEEP_TIME) # Rate Limit 방지

if __name__ == "__main__":
    # 폴더가 없으면 생성
    os.makedirs("./test_images/target", exist_ok=True)
    os.makedirs("./test_images/candidates", exist_ok=True)
    
    run_test()