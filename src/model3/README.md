# Phonetic Similarity Model

상표 간 **발음 유사도**를 자동으로 계산하는 AI 모델입니다.

---

## 📂 프로젝트 구조

```
Phonetic-Similarity/
├── code/
│   ├── converter.py    # 발음 변환 모듈 (영어→한글)
│   ├── scorer.py       # 유사도 계산 모듈 (3-Tier Logic)
│   ├── evaluate.py     # 정답지 기반 성능 평가
│   └── inference.py    # 단건/다건 테스트 실행
├── data/
│   ├── goldenset.xlsx  # 정답 데이터 (49건)
│   └── report.xlsx     # 평가 결과
├── .env                # API 키 설정 (개인별 생성 필요)
├── requirements.txt    # 필요 라이브러리
└── README.md           # 이 파일
```

---

## 🚀 Quick Start (2단계)

### Step 1: 가상환경 설정 및 설치
```bash
# 1) 가상환경 생성
python -m venv venv

# 2) 가상환경 활성화
.\venv\Scripts\Activate.ps1      # PowerShell (권장)
# 또는
.\venv\Scripts\activate.bat      # CMD

# 3) 프롬프트 확인 (venv) 표시되면 성공
(venv) PS C:\...\model3_latest>

# 4) 라이브러리 설치
pip install -r requirements.txt
```

**가상환경 비활성화:**
```bash
deactivate
```

### Step 2: API 설정 확인
✅ **이 배포판에는 `.env` 파일이 이미 포함되어 있습니다!**  
Azure OpenAI API 설정이 완료된 상태이므로 **추가 설정 없이 바로 실행 가능**합니다.

**포함된 설정:**
- Azure OpenAI API Key
- Endpoint: https://phonetic-sim.openai.azure.com/
- Deployment: gpt-5.1-chat
- API Version: 2025-01-01-preview

### Step 3: 실행

**A) 성능 평가 (개발자용)**
```bash
python code/evaluate.py
```
→ `data/goldenset.xlsx`의 49건 정답지로 모델 정확도 측정  
→ 결과: `data/report.xlsx`

**B) 시연/테스트 (팀원용)**
```bash
python code/inference.py
```
→ 모드 선택:
  - `1`: 미리 정의된 리스트 일괄 테스트
  - `2`: 직접 상표명 입력하여 테스트

---

## 📊 판정 기준

| 점수 | 등급 | 해석 |
|------|------|------|
| 80+ | **High** | 유사 가능성 높음 (침해 위험) |
| 50~79 | Medium | 추가 검토 필요 |
| 0~49 | Low | 유사하지 않음 |

---

## 🔧 주요 모듈

### `converter.py`
- 영어 상표 → 한글 발음 변환
- 한글 상표 → 표준 발음 변환 (g2pk)

### `scorer.py`
- 3-Tier Decision Logic (Microscope/Telescope/Inclusion)
- Jaro-Winkler + Jamo + Partial Ratio 가중 계산

---

## 📝 예시

```
[INPUT] Brand A: NIKE
[INPUT] Brand B: NUKE

[CONVERT] A: NIKE -> 나이키
[CONVERT] B: NUKE -> 누크

[RESULT]
   Score: 72.50 / 100
   Grade: Medium
```
