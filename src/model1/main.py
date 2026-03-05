import os
import glob
import config
from pipeline import TrademarkRemover

def main():
    # 1. 파이프라인 초기화 (모델 로딩)
    print("========================================")
    print("   Trademark Remover Pipeline Start     ")
    print("========================================")
    remover = TrademarkRemover()

    # 2. 테스트 이미지 목록 가져오기
    # config.TEST_IMAGE_DIR 폴더 안의 jpg, png, jfif 파일들을 찾습니다.
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.jfif']
    image_paths = []
    
    for ext in image_extensions:
        # glob를 사용하여 패턴에 맞는 파일을 찾습니다.
        search_path = os.path.join(config.TEST_IMAGE_DIR, ext)
        found_files = glob.glob(search_path)
        image_paths.extend(found_files)

    print(f"\n[INFO] 총 {len(image_paths)}개의 이미지를 찾았습니다: {config.TEST_IMAGE_DIR}")

    if len(image_paths) == 0:
        print("[ERROR] 테스트할 이미지가 없습니다. config.py의 경로를 확인해주세요.")
        return

    # 3. 각 이미지 처리
    for img_path in image_paths:
        try:
            remover.process_image(img_path)
        except Exception as e:
            print(f"[ERROR] 처리 중 오류 발생 ({os.path.basename(img_path)}): {e}")

    print("\n========================================")
    print("        All Jobs Completed !!           ")
    print(f"   결과 확인: {config.OUTPUT_DIR}")
    print("========================================")

if __name__ == "__main__":
    main()
