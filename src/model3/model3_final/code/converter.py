"""
converter.py - Phonetic Similarity Analyzer v8.3
================================================
Model: gpt-5.1-chat (High-Reasoning)
Update: 
  1. Cluster Gemination: Consonant + R/L -> 'ㄹ' Patchim + 'ㄹ' Initial.
     (e.g., Srock -> 슬락, Slock -> 슬락).
  2. Strict S-Rule: S -> 'ㅅ'.
  3. Liquid Unification: R = L = 'ㄹ'.
"""

import os, re, json
from dotenv import load_dotenv
from g2pk import G2p
from openai import AzureOpenAI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ✅ 자음+R/L 통합 규칙(RULE 7) 추가
SYSTEM_PROMPT = """You are a Korean Trademark Phonetic Expert.

### [CRITICAL: INPUT TYPE HANDLING RULES]

#### **TYPE A: PURE KOREAN (Hangul Only)**
- **Rule:** Read EXACTLY as written. DO NOT alter based on English counterparts.
- **Process:** Literal Reading -> Standard Pronunciation (via g2pk).
- **Example:** "하겐데스" -> ["하겐데스"] (Immutable), "국물" -> ["궁물"] (Assimilation).

#### **TYPE B: PURE ENGLISH (Letters Only)**
- **RULE 1 (The Rule):**
  - 'The' + **Vowel** -> **"디"** (The Ocean -> 디오션).
  - 'The' + **Consonant** -> **"더"** (The Man -> 더맨).

- **RULE 2 (Suffix Standardization):**
  - **-tion / -cian / -ceon:** Always read as **"션"** (Shun).
    - **Example:** "Diocian" -> ["디오션"].
    - **Example:** "Ocean" -> ["오션"].
  - **-on:** After a consonant, read as **"온"** (On). (e.g., Canon -> 캐논).
  - **-op / -ock:** After a consonant, read 'O' as 'Ah' (**"압" / "악"**).
    - **Example:** "Pop" -> ["팝"] (NOT 폽).
    - **Example:** "Slock" -> ["슬락"].

- **RULE 3 (F-P Neutralization):**
  - **'F' is perceived identically to 'P' ('ㅍ').** NEVER map 'F' to 'ㅎ'.
  - **Example:** "Fine" -> ["파인"], "FILA" -> ["필라"].

- **RULE 4 (Silent R):**
  - If 'R' is followed by a **Consonant** or is at the **End of Word**, it is **SILENT**.
  - **Example:** "Cartok" -> "Ca-tok" -> ["카톡"].
  - **Example:** "Ginkor" -> ["징코"].
  - **Example:** "Park" -> ["파크"].

- **RULE 5 (Liquid Unification R=L='ㄹ'):**
  - In Korean, **'R' and 'L' are NOT distinguished** when followed by a vowel.
  - Map BOTH to **'ㄹ'**.
  - **Example:** "Rock" -> ["락"].
  - **Example:** "Lock" -> ["락"].

- **RULE 6 (S-Handling - STRICT):**
  - In **Pure English** inputs, 'S' must ALWAYS be mapped to **'ㅅ'** (S/Sh).
  - **NEVER** map 'S' to 'ㅈ' (Z/J).
  - **Example:** "Super" -> ["수퍼"].
  - **Example:** "Bus" -> ["버스"].

- **RULE 7 (Consonant + Liquid Cluster Gemination):**
  - **Logic:** If a Consonant (C) is followed by 'R' or 'L' and a vowel, **FORCE 'ㄹ' GEMINATION**.
  - **Pattern:** `C` + `R/L` + `Vowel` -> `[C]을` + `ㄹ[Vowel]`.
  - **Why:** To make 'S-Rock' and 'S-Lock' sound identical in phonetic matching.
  - **Example (S+L):** "Slock" -> "Sl" -> "슬" + "Lock" -> "락" => ["슬락"].
  - **Example (S+R):** "Srock" -> "Sl" (Treat R as L cluster) -> "슬" + "Rock" -> "락" => ["슬락"].
  - **Target Application:**
    - "Asrock" -> "A" + "S-rock" -> "애" + "슬락" => **["애슬락"]**.
    - "Slock" -> **["슬락"]**.
    - "Cream" -> "C-ream" -> **["클림"]** (For matching purpose).
    - "Bread" -> "B-read" -> **["블레드"]**.

#### **TYPE C: MIXED / SYMBOLS / NUMBERS**
- **Rule:** Follow Market Consensus.
- **Example:** "L'EAU" -> ["로우"], "GS25" -> ["지에스이십오"], "Gen.G" -> ["젠지"].

### [ANCHOR & SYNC RULES]
- **-talk Suffix:** Always '톡'. (Katalk -> ["카톡"]).

### [OUTPUT FORMAT]
- Return ONLY JSON: {"korean": ["..."]}  
"""
## 위에 Return ONLY JSON: {"korean": ["..."]} 이부분 수정함.<!-- [Fix 2026-02-19] Changed from {"korean_a":..., "korean_b":...} to single key to prevent empty list errors -->
try:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
except:
    client = None

g2p = G2p()

def clean_hangul(text_list):
    if not isinstance(text_list, list): text_list = [text_list]
    cleaned = [ ''.join(re.findall(r'[가-힣]+', str(s))) for s in text_list ]
    return [c for c in cleaned if c] if any(cleaned) else [""]

def apply_korean_phonetics(text_list):
    result = []
    for text in text_list:
        if text and re.match(r'^[가-힣]+$', text):
            try:
                pronounced = g2p(text).strip()
                pronounced = ''.join(re.findall(r'[가-힣]+', pronounced))
                result.append(pronounced if pronounced else text)
            except:
                result.append(text)
        else:
            result.append(text)
    unique_result = list(dict.fromkeys(result))
    return unique_result if unique_result else [""]

def convert_single(brand_text):
    """
    [Updated - 팀원 공유용] 단일 상표 변환 함수 (Isolation Mode)
    - 기존 convert_pair에서 분리됨.
    - 한 번에 하나의 상표만 처리하여 GPT가 A와 B를 혼동하거나 섞는 문제(Cross-Contamination) 방지.
    """
    brand_text = brand_text.strip()
    if not brand_text: return [""]
    
    if client:
        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                # Temperature 0.0을 유지하여 언제나 동일한 결과 보장
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, 
                          {"role": "user", "content": f"Brand: {brand_text}"}]
            )
            raw = response.choices[0].message.content.strip()
            
            parsed = None
            clean = re.sub(r'```json\s*|```\s*', '', raw)
            start, end = clean.find('{'), clean.rfind('}')
            
            if start != -1 and end != -1:
                json_str = clean[start:end+1]
                try:
                    parsed = json.loads(json_str)
                except json.JSONDecodeError:
                    try:
                        # JSON 복구 시도
                        json_str_fixed = json_str.replace('\\"', '"').replace("'", '"')
                        parsed = json.loads(json_str_fixed)
                    except:
                        pass
            
            if parsed:
                # [Fix 2026-02-19] GPT가 {"korean": [], "korean_b": ["라온"]} 처럼 빈 리스트를 먼저 줄 경우 대비
                # 유효한(값이 있는) 리스트를 우선 찾고, 없으면 마지막 리스트라도 반환
                valid_result = None
                
                for key in parsed:
                    if isinstance(parsed[key], list):
                        k_list = clean_hangul(parsed[key])
                        if any(k_list) and k_list != [""]:
                            valid_result = k_list
                            break # 유효한 값을 찾았으면 즉시 반환
                
                if valid_result:
                    return apply_korean_phonetics(valid_result)
                
                # 만약 유효한 값이 없으면 첫 번째 리스트라도 사용 (혹은 원본)
                for key in parsed:
                    if isinstance(parsed[key], list):
                        k_list = clean_hangul(parsed[key])
                        return apply_korean_phonetics(k_list)
            
            # print(f"[WARN] JSON 파싱 실패 (Single) - 원본: {raw[:50]}...")
                
        except Exception as e:
            print(f"[WARN] API 변환 실패 (Single): {e}")
            
    return apply_korean_phonetics([brand_text])

def convert_pair(brand_a, brand_b):
    """
    [Refactored 2026-02-17 - 팀원 공유용]
    
    [수정 이유]
    기존: A와 B를 한번에 프롬프트에 넣고 비교 요청 -> GPT가 두 상표를 모두 출력.. 비교할때 같이 상표 두쌍을 한번에 섞어서 반환하는 심각한 오류(Cross-Contamination) 발생.
          (예: A=['공감', '공감한의원'], B=['공감', '공감한의원'] 처럼 A+B가 양쪽에 들어감)
          
    [수정 내용]
    수정: convert_single()을 두 번 호출하여 A와 B를 완전히 독립적으로 변환한 뒤 합침.
          API 호출 횟수는 2배가 되지만, 데이터 무결성(Data Integrity)을 보장하도록 수정함.
    """
    # 1. 상표 A 단독 변환 (Isolation Mode)
    korean_a = convert_single(brand_a)
    
    # 2. 상표 B 단독 변환 (Isolation Mode)
    korean_b = convert_single(brand_b)
    
    return {"korean_a": korean_a, "korean_b": korean_b}

# ========================================================================================
# [Reference] 변경 전 코드 (Legacy Code)
# - 아래 코드는 두 상표를 한 번에 처리하던 구버전 로직입니다. (참고용)
#
# def convert_pair_legacy(brand_a, brand_b):
#     brand_a, brand_b = brand_a.strip(), brand_b.strip()
#     
#     if client:
#         try:
#             # [문제점] 두 브랜드를 한 프롬프트에 같이 넣음 -> 상호 간섭 발생
#             response = client.chat.completions.create(
#                 model=DEPLOYMENT_NAME,
#                 # Temperature 0.0을 유지하여 언제나 동일한 결과 보장
#                 messages=[{"role": "system", "content": SYSTEM_PROMPT}, 
#                           {"role": "user", "content": f"Brand A: {brand_a}\\nBrand B: {brand_b}"}]
#             )
#             raw = response.choices[0].message.content.strip()
#             
#             parsed = None
#             clean = re.sub(r'```json\s*|```\s*', '', raw)
#             start, end = clean.find('{'), clean.rfind('}')
#             
#             if start != -1 and end != -1:
#                 json_str = clean[start:end+1]
#                 try:
#                     parsed = json.loads(json_str)
#                 except json.JSONDecodeError:
#                     try:
#                         json_str_fixed = json_str.replace('\\"', '"').replace("'", '"')
#                         parsed = json.loads(json_str_fixed)
#                     except json.JSONDecodeError:
#                         try:
#                             korean_a_match = re.search(r'"korean_a"\s*:\s*\[([^\]]+)\]', json_str)
#                             korean_b_match = re.search(r'"korean_b"\s*:\s*\[([^\]]+)\]', json_str)
#                             if korean_a_match and korean_b_match:
#                                 k_a_raw = korean_a_match.group(1)
#                                 k_b_raw = korean_b_match.group(1)
#                                 k_a_list = re.findall(r'"([^"]+)"', k_a_raw)
#                                 k_b_list = re.findall(r'"([^"]+)"', k_b_raw)
#                                 parsed = {"korean_a": k_a_list, "korean_b": k_b_list}
#                         except:
#                             pass
#             
#             if parsed:
#                 k_a = clean_hangul(parsed.get("korean_a", []))
#                 k_b = clean_hangul(parsed.get("korean_b", []))
#                 return {"korean_a": apply_korean_phonetics(k_a), 
#                         "korean_b": apply_korean_phonetics(k_b)}
#             else:
#                 print(f"[WARN] JSON 파싱 실패 - 원본 응답: {raw[:100]}...")
#                 
#         except Exception as e:
#             print(f"[WARN] API 변환 실패: {e}")
#             
#     return {"korean_a": apply_korean_phonetics([brand_a]), "korean_b": apply_korean_phonetics([brand_b])}
# ========================================================================================