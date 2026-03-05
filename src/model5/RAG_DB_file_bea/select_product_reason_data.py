import os
import json
from openai import AzureOpenAI
from sqlalchemy import create_engine, text

from dotenv import load_dotenv

load_dotenv()

# DB 환경 설정
DB_CONNECTION_INFO = "postgresql://tipadmin:team1%21%40%23%24@tip-db.postgres.database.azure.com:5432/postgres"

engine = create_engine(DB_CONNECTION_INFO)

# Azure 임베딩 모델 설정
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "")
)

# Text => Vector 임베딩
def get_embedding(text_to_embed):
    deployment_name = "text-embedding-3-large" 
    
    response = client.embeddings.create(
        input=[text_to_embed],
        model=deployment_name
    )
    
    # 1차원 리스트로 변환하여 반환
    return response.data[0].embedding

# TBL_REASON_TRADEMARK (거절 사유 정보)
def search_similar_contents(query_text):
    
    # 입력 텍스트 임베딩 생성
    query_vector = get_embedding(query_text)
    
    # SQL 쿼리 작성 (pgvector의 <=> 연산자는 코사인 거리를 계산함)
    # 유사도가 높을수록 거리는 작으므로 ORDER BY distance ASC 사용 (오름차순)
    
    # 아래 SELECT 다음에 나열된것중에 사용하시믄 됩니다 행님
    query = text("""
        SELECT 
            patent_id,
            korean_name,
            english_name,
            cleaned_content, 
            reason_tags,
            product_tags,
            1 - (cleaned_content_vec <=> :vector) AS similarity
        FROM tbl_reason_trademark
        ORDER BY cleaned_content_vec <=> :vector
        LIMIT :limit
    """)
    
    # 데이터베이스 실행
    with engine.connect() as conn:
        result = conn.execute(query, {
            "vector": str(query_vector),
            "limit": 20   # 유사도 높은 상위 20개
        })
        
        return result.fetchall()

# --- 실행 예시 ---
if __name__ == "__main__":
    search_query = "화장품 상표 거절 사례 찾아줘"
    top_results = search_similar_contents(search_query)

    print(f"'{search_query}'와(과) 유사한 상위 20개 결과:\n")
    for row in top_results:
        print(f"ID: {row.patent_id} | 유사도: {row.similarity:.4f}")
        print("-" * 50)