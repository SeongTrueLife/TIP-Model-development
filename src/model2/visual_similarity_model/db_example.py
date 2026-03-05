from model_utils import load_trained_model, get_embedding, get_cosine_similarity
import torch
import numpy as np

# 1. 초기 세팅 (모델 로드는 서비스 시작 시 한 번만)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
weight_path = 'resnet50_triplet_final.pth'
model, _ = load_trained_model(weight_path) # model_utils 구조에 맞춰 수정

# [Task 1] DB 인덱싱 (저장용 벡터 추출)
# 15만 장의 이미지를 순회하며 아래 과정을 반복하여 DB에 저장하세요.
try:
    img_vector = get_embedding('sample_logo.jpg', model, device)
    print(f"추출된 벡터 타입: {type(img_vector)}, 크기: {img_vector.shape}")
    # --> img_vector는 numpy.ndarray (128,) 형태입니다.
    # --> 이를 DB의 FLOAT ARRAY 또는 VECTOR(128) 컬럼에 저장하세요.
except Exception as e:
    print(f"벡터 추출 실패: {e}")

# [Task 2] 유사도 검색 (사용자 쿼리)
try:
    query_vector = get_embedding('user_upload.jpg', model, device)
    
    # DB에서 불러온 기존 데이터라고 가정
    db_vector = img_vector 
    
    # 두 벡터 간 코사인 유사도 계산
    similarity = get_cosine_similarity(query_vector, db_vector)
    
    print(f"📊 유사도 결과: {similarity:.4f}")
    if similarity > 0.8:
        print("결과: 매우 유사한 로고입니다.")
    elif similarity > 0.5:
        print("결과: 유사할 가능성이 있습니다.")
    else:
        print("결과: 다른 로고일 확률이 높습니다.")
        
except Exception as e:
    print(f"검색 프로세스 에러: {e}")