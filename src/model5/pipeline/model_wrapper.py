"""
Model Wrapper for Integration Pipeline
======================================
이 모듈은 분산된 각 모델(Model 2, 3, 4)을 하나의 인터페이스로 호출할 수 있도록 감싸는 역할을 합니다.
경로 문제(sys.path)를 해결하고, 각 모델의 핵심 함수를 import하여 사용합니다.
"""

import sys
import os
import torch
import numpy as np
from pathlib import Path

# --- [Path Setup] ---
# 프로젝트 루트 경로 (c:\ms_ai_school\project\Trademark)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Model 2 Path
MODEL2_PATH = PROJECT_ROOT / "model2" / "visual_similarity_model"
sys.path.append(str(MODEL2_PATH))

# Model 3 Path
MODEL3_PATH = PROJECT_ROOT / "model3" / "model3_final" / "code"
sys.path.append(str(MODEL3_PATH))

# Model 4 Path
MODEL4_PATH = PROJECT_ROOT / "model4" / "semanticmodel_final0210"
sys.path.append(str(MODEL4_PATH))


# --- [Model Imports] ---
try:
    # Model 2
    from model_utils import load_trained_model, get_embedding as get_vis_embedding, get_cosine_similarity
    
    # Model 3
    import scorer as m3_scorer
    import converter as m3_converter
    
    # Model 4
    # trademark_analysis.py의 함수들을 직접 import
    # 주의: config.py 등이 MODEL4_PATH에 있으므로 sys.path 추가 필수
    from trademark_analysis import generate_description, get_embedding as get_sem_embedding
    
    print("[Success] All models imported successfully.")
except ImportError as e:
    print(f"[Error] Failed to import models: {e}")
    print("Check sys.path settings in model_wrapper.py")
    raise e


# --- [Model 2: Visual Similarity] ---
class VisualModelWrapper:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.weight_path = MODEL2_PATH / "resnet50_triplet_final.pth"
        
        if not self.weight_path.exists():
            raise FileNotFoundError(f"Model 2 weights not found at {self.weight_path}")
            
        print(f"[Model 2] Loading weights from {self.weight_path}...")
        self.model = load_trained_model(str(self.weight_path), self.device)
        self.model.eval()

    def get_score(self, target_img_path: str, cited_img_path: str) -> float:
        """
        두 이미지 경로를 받아 유사도(0.0 ~ 1.0)를 반환합니다.
        """
        try:
            emb1 = get_vis_embedding(target_img_path, self.model, self.device)
            emb2 = get_vis_embedding(cited_img_path, self.model, self.device)
            
            # Cosine Similarity Calculation
            score = get_cosine_similarity(emb1, emb2)
            
            # Clip result to [0.0, 1.0] just in case
            return float(np.clip(score, 0.0, 1.0))
        except Exception as e:
            print(f"[Model 2 Error] {e}")
            return 0.0


# --- [Model 3: Phonetic Similarity] ---
class PhoneticModelWrapper:
    def __init__(self):
        pass # 별도 로딩 필요 없음 (Rule-based + API)

    def get_score(self, target_text: str, cited_text: str) -> float:
        """
        두 텍스트를 받아 유사도(0 ~ 100)를 반환합니다.
        """
        try:
            # 1. 발음 변환 (converter.convert_pair는 API 호출 없이 로컬 룰베이스 변환 수행)
            # 주의: converter.py가 OpenAI API를 쓰는지 확인 필요. 
            # (converter.py 코드를 보면 g2pk 등 라이브러리 사용. 만약 GPT 쓰면 비용 발생)
            
            # Model 3의 main.py 로직을 참고하여 구현
            pair = m3_converter.convert_pair(target_text, cited_text)
            list_a = pair['korean_a']
            list_b = pair['korean_b']
            
            # Fragment Filter
            max_len_a = max(len(p) for p in list_a) if list_a else 0
            max_len_b = max(len(p) for p in list_b) if list_b else 0
            
            valid_a = [p for p in list_a if len(p) >= max_len_a * 0.8]
            valid_b = [p for p in list_b if len(p) >= max_len_b * 0.8]
            
            best_score = 0.0
            
            # Cross Validation
            for p_a in valid_a:
                for p_b in valid_b:
                    score, _, _ = m3_scorer.compare(p_a, p_b)
                    if score > best_score:
                        best_score = score
            
            # 변환 결과 문자열 생성 (예: "A:['나이키'] vs B:['누크']")
            trans_info = f"A:{list_a} vs B:{list_b}"
            return float(best_score), trans_info
            
        except Exception as e:
            print(f"[Model 3 Error] {e}")
            return 0.0, f"Error: {e}"


# --- [Model 4: Semantic Similarity] ---
class SemanticModelWrapper:
    def __init__(self):
        # API Client는 trademark_analysis.py 내부에서 초기화됨
        pass

    def get_score(self, target_img_path: str, cited_img_path: str) -> tuple[float, str]:
        """
        두 이미지를 받아 (관념 유사도 점수, 타겟 이미지 묘사)를 반환합니다.
        주의: GPT-4 Vision API 호출 비용 발생
        """
        try:
            # 1. Generate Description (Vision API)
            desc1 = generate_description(target_img_path)
            desc2 = generate_description(cited_img_path)
            
            if not desc1 or not desc2:
                print("[Model 4] Failed to generate description.")
                return 0.0, ""
            
            # 2. Get Embedding (Embedding API)
            vec1 = get_sem_embedding(desc1)
            vec2 = get_sem_embedding(desc2)
            
            if not vec1 or not vec2:
                print("[Model 4] Failed to generate embedding.")
                return 0.0, ""
                
            # 3. Calculate Cosine Similarity
            # vec1, vec2 are lists -> convert to numpy
            v1 = np.array(vec1).reshape(1, -1)
            v2 = np.array(vec2).reshape(1, -1)
            
            from sklearn.metrics.pairwise import cosine_similarity
            score = cosine_similarity(v1, v2)[0][0]
            
            return float(score), desc1
            
        except Exception as e:
            print(f"[Model 4 Error] {e}")
            return 0.0, ""
