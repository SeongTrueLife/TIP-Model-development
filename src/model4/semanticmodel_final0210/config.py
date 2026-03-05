import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Azure OpenAI 설정
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2024-05-01-preview")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT", "")

# 모델 설정
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.1-chat")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# 경로 설정
TARGET_DIR = os.getenv("TARGET_DIR", "./test_images/target")
CANDIDATE_DIR = os.getenv("CANDIDATE_DIR", "./test_images/candidates")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "data.jsonl")

# Rate Limit 설정
SLEEP_TIME = float(os.getenv("SLEEP_TIME", "0.5"))

# 설정값 검증 함수
def validate_config():
    """필수 설정값이 있는지 확인"""
    if not AZURE_API_KEY:
        raise ValueError("AZURE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    if not AZURE_ENDPOINT:
        raise ValueError("AZURE_ENDPOINT가 설정되지 않았습니다. .env 파일을 확인하세요.")
    return True
