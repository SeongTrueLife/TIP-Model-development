# [Model 3] 발음 유사도 점수 0점 오류 수정 가이드 (2026-02-19)

이 문서는 Model 3 (Phonetic Similarity)에서 **발음 변환이 제대로 되지 않아 점수가 0점으로 나오는 오류**를 해결하기 위한 수정 사항을 담고 있습니다.

## ⚠️ 문제 현상
- `raw_pho` (발음 유사도) 점수가 0점으로 나오는 비율이 38% -> 48%로 증가함.
- `DB` vs `DB`, `RAON` vs `RAON SECURE` 등 명확한 동일/유사 상표임에도 변환 결과가 `['']` (빈 문자열)로 반환되어 0점이 산출됨.

## 🔍 원인 분석
1. **시스템 프롬프트 불일치**: 
   - `converter.py` 코드는 상표를 하나씩 변환(`convert_single`)하도록 업데이트되었으나, 프롬프트는 여전히 **"두 개의 결과(`korean_a`, `korean_b`)를 반환하라"**고 지시하고 있었음.
2. **LLM의 강제 응답**:
   - GPT는 지시대로 두 개의 키를 생성하기 위해, 입력받지 않은 나머지 하나를 빈 리스트(`[]`)로 채워서 반환함.
   - 예: `Brand: RAON` -> GPT 응답: `{"korean_a": [], "korean_b": ["라온"]}`
3. **파싱 로직 오류**:
   - 코드에서 JSON 응답을 파싱할 때, 빈 리스트(`korean_a`)를 먼저 발견하여 변환 결과로 사용해버림 -> 0점 발생.

## ✅ 수정 내용 (`model3/model3_final/code/converter.py`)

### 1. `SYSTEM_PROMPT` 수정
- **변경 전**: `Return ONLY JSON: {"korean_a": ["..."], "korean_b": ["..."]}`
- **변경 후**: `Return ONLY JSON: {"korean": ["..."]}`
- **설명**: 단일 상표 변환에 맞게 출력 형식을 간소화하여 불필요한 빈 리스트 생성을 방지함.

### 2. `convert_single` 함수 파싱 로직 개선
- **변경 전**: JSON 키를 순회하며 첫 번째 리스트를 무조건 반환.
- **변경 후**: 
  - 리스트 내에 **유효한 값(빈 문자열 아님)**이 있는지 검사.
  - 유효한 값이 있는 리스트를 우선적으로 선택하여 반환.
  - GPT가 실수로 이상한 키(`korean_b` 등)를 주더라도 내용이 있으면 정상 처리되도록 안전장치 추가.

## 🚀 적용 방법
1. 첨부된 `converter.py` 파일로 기존 파일을 덮어쓰거나, 위 수정 내용을 직접 코드에 반영하세요.
2. `src.model5.pipeline.run_batch_inference`를 다시 실행하여 `raw_pho` 점수가 정상적으로 나오는지 확인하세요.
   - 테스트 커맨드: `python -m src.model5.pipeline.run_batch_inference --limit 3 --split test`

---
**작성자**: AI Assistant
**날짜**: 2026-02-19
