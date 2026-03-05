import os
import sys
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageDraw, ImageFont

# 환경 변수 로드
load_dotenv()

# 설정값 가져오기
KEY = os.getenv("VISION_KEY")
ENDPOINT = os.getenv("VISION_ENDPOINT")

def get_client():
    if not KEY or not ENDPOINT or "PASTE" in KEY:
        print("오류: .env 파일에 올바른 VISION_KEY와 VISION_ENDPOINT를 설정해주세요.")
        sys.exit(1)
    
    credentials = CognitiveServicesCredentials(KEY)
    client = ComputerVisionClient(ENDPOINT, credentials)
    return client

def draw_brands(image_path, brands, output_path="detected_brands.jpg"):
    """
    이미지에 브랜드 박스를 그리고 저장합니다.
    """
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # 폰트 설정 (기본 폰트 사용, 실패 시 시스템 폰트 시도)
        try:
            # 윈도우 기본 폰트
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        print(f"\n[결과] 총 {len(brands)}개의 브랜드를 찾았습니다.")

        for brand in brands:
            print(f" - 브랜드명: {brand.name}, 신뢰도: {brand.confidence * 100:.2f}%")
            
            # 박스 좌표 (API는 left, top, width, height를 반환할 수 있음)
            # rectangle은 [x0, y0, x1, y1] 필요
            rect = brand.rectangle
            left = rect.x
            top = rect.y
            right = rect.x + rect.w
            bottom = rect.y + rect.h
            
            # 박스 그리기 (빨간색, 두께 3)
            draw.rectangle([left, top, right, bottom], outline="red", width=4)
            
            # 텍스트 배경 및 텍스트
            text = f"{brand.name} ({brand.confidence*100:.1f}%)"
            
            # 텍스트 크기 계산 (Pillow 버전에 따라 다름)
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((left, top), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            else:
                text_w, text_h = draw.textsize(text, font=font)
            
            # 텍스트 배경
            draw.rectangle([left, top - text_h - 10, left + text_w + 10, top], fill="red")
            # 텍스트 쓰기
            draw.text((left + 5, top - text_h - 5), text, fill="white", font=font)

        image.save(output_path)
        print(f"\n결과 이미지가 저장되었습니다: {os.path.abspath(output_path)}")
        
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")

def main():
    client = get_client()
    
    # 이미지 파일 경로 입력 받기
    print("분석할 이미지 파일 경로를 입력하세요 (기본값: test.jpg):")
    image_path = input().strip()
    if not image_path:
        image_path = "test.jpg"
    
    # 따옴표 제거
    image_path = image_path.replace('"', '').replace("'", "")

    if not os.path.exists(image_path):
        print(f"오류: 파일을 찾을 수 없습니다 -> {image_path}")
        print("팁: 테스트할 이미지를 이 폴더에 넣거나 절대 경로를 입력하세요.")
        return

    print(f"\n'{image_path}' 분석 중...")
    
    try:
        with open(image_path, "rb") as image_stream:
            # 브랜드 감지 실행
            analysis = client.analyze_image_in_stream(
                image_stream,
                visual_features=[VisualFeatureTypes.brands]
            )
            
        if analysis.brands:
            draw_brands(image_path, analysis.brands)
        else:
            print("감지된 브랜드가 없습니다.")
            
    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")
        print("팁: .env 파일의 키와 엔드포인트가 정확한지, 인터넷이 연결되어 있는지 확인하세요.")

if __name__ == "__main__":
    main()
