"""
[Node 3] Legal Retriever (The Librarian)

Role:
    Node 2에서 생성된 쿼리들을 사용하여 Vector DB(PostgreSQL)에서 유사 판례를 검색합니다.
    검색된 결과는 중복을 제거하고 구조화된 텍스트로 변환되어 Node 4(Judge)에게 전달됩니다.

Type:
    RAG (Vector Search + Deduplication)
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from openai import AzureOpenAI
from dotenv import load_dotenv

from ..state import AgentState

# 환경 변수 로드 (src/model5/.env)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# --- [Configuration] ---
# DB 연결 정보 (팀원이 제공한 정보 기반, 실제 값은 .env 권장)
DEFAULT_DB_CONN = "postgresql://tipadmin:team1%21%40%23%24@tip-db.postgres.database.azure.com:5432/postgres"
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", DEFAULT_DB_CONN)

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_EMBEDDING", "text-embedding-3-large")
AZURE_OPENAI_API_VERSION = "2024-12-01-preview"

# --- [Global Resources Initialization] ---
engine = None
client = None

try:
    # 1. SQLAlchemy Engine 생성
    engine = create_engine(DB_CONNECTION_STRING)
    
    # 2. Azure OpenAI Client 생성 (임베딩용)
    if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    else:
        print("[Node 3 Warning] Azure OpenAI credentials not found.")

except Exception as e:
    print(f"[Node 3 Error] Initialization failed: {e}")


def get_embedding(text_to_embed: str) -> List[float]:
    """
    텍스트를 임베딩 벡터로 변환합니다.
    """
    if not client:
        return []
        
    try:
        response = client.embeddings.create(
            input=[text_to_embed],
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Node 3 Error] Embedding generation failed: {e}")
        return []


def node_3_retriever(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node Function
    rag_queries를 사용하여 DB 검색 후 rag_contexts를 반환합니다.
    """
    
    # 1. 입력 데이터 확인
    rag_queries = state.get("rag_queries", {})
    queries = rag_queries.get("queries", [])
    
    # 쿼리가 없거나 DB 연결이 안 되어 있으면 빈 결과 반환 (Fail-safe)
    if not queries:
        print("[Node 3] No queries provided.")
        return {"rag_contexts": []}
    
    if not engine:
        print("[Node 3] DB Engine is not initialized.")
        return {"rag_contexts": ["(시스템 오류: DB 연결 실패로 인해 검색 결과를 불러올 수 없습니다.)"]}

    unique_results = {} # Deduplication Buffer: {patent_id: row}
    
    # 2. SQL 쿼리 준비 (Cosine Distance)
    # 1 - (A <=> B) = Cosine Similarity (Approx.)
    # team code reference: 1 - (cleaned_content_vec <=> :vector)
    sql_query = text("""
        SELECT 
            patent_id, 
            cleaned_content, 
            reason_tags, 
            product_tags,
            1 - (cleaned_content_vec <=> :vector) AS similarity
        FROM tbl_reason_trademark
        ORDER BY cleaned_content_vec <=> :vector
        LIMIT :limit
    """)

    # 3. 검색 실행 (Iterative Search)
    try:
        with engine.connect() as conn:
            for q_text in queries:
                # 임베딩 생성
                vector = get_embedding(q_text)
                if not vector:
                    continue
                
                # DB 쿼리 실행
                # 쿼리 하나당 상위 5개만 조회 (다양성 확보)
                rows = conn.execute(sql_query, {
                    "vector": str(vector), # pgvector requires string representation
                    "limit": 5
                }).fetchall()
                
                # 결과 수집 및 중복 제거
                for row in rows:
                    if row.patent_id not in unique_results:
                        unique_results[row.patent_id] = row
                        
    except Exception as e:
        print(f"[Node 3 Error] DB Execution failed: {e}")
        return {"rag_contexts": [f"(시스템 오류: 검색 중 DB 에러 발생 - {str(e)})"]}

    # 4. 결과 정렬 및 포맷팅
    # 유사도(similarity) 기준으로 내림차순 정렬
    sorted_rows = sorted(unique_results.values(), key=lambda x: x.similarity, reverse=True)
    
    # 상위 10개만 선택 (Context Window 고려)
    top_rows = sorted_rows[:10]
    
    formatted_contexts = []
    for row in top_rows:
        # LLM이 참고하기 좋은 포맷으로 변환
        context_str = (
            f"[Case ID: {row.patent_id}]\n"
            f"- Similarity: {row.similarity:.4f}\n"
            f"- Tags: {row.reason_tags} (Product: {row.product_tags})\n"
            f"- Content: {row.cleaned_content}\n"
        )
        formatted_contexts.append(context_str)
        
    print(f"[Node 3] Retrieved {len(formatted_contexts)} unique cases.")

    # 5. 결과 반환 (State Update)
    return {
        "rag_contexts": formatted_contexts
    }
