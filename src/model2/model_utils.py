import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np

class ResNet50TripletNet(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        backbone = models.resnet50()
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        self.fc = nn.Linear(2048, embedding_dim)
    
    def forward(self, x):
        x = self.backbone(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return F.normalize(x, p=2, dim=1)

def load_trained_model(weight_path, device):
    if not os.path.exists(weight_path):
        raise FileNotFoundError(f"모델 파일이 없습니다: {weight_path}")
    
    model = ResNet50TripletNet(embedding_dim=128).to(device)
    model.load_state_dict(torch.load(weight_path, map_location=device))
    model.eval()
    return model

# 이미지 전처리 설정
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def get_embedding(image_path, model, device):
    """이미지를 128차원 벡터로 변환 (에러 처리 포함)"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
    
    try:
        img = Image.open(image_path).convert('RGB')
        img_t = preprocess(img).unsqueeze(0).to(device)
        
        with torch.no_grad():
            embedding = model(img_t)
        return embedding.cpu().numpy().flatten()
    except Exception as e:
        raise RuntimeError(f"이미지 처리 중 에러 발생: {e}")

def get_cosine_similarity(v1, v2):
    """벡터 내적을 통한 코사인 유사도 계산"""
    return np.dot(v1, v2)
  