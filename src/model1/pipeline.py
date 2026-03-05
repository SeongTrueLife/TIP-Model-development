import os
import cv2
import numpy as np
from ultralytics import YOLO, SAM
import config

class TrademarkRemover:
    def __init__(self):
        """
        모델 초기화: YOLO v11과 SAM 2 모델을 로드합니다.
        """
        print(f"[INFO] YOLO 모델 로딩 중: {config.YOLO_MODEL_PATH}")
        self.yolo_model = YOLO(config.YOLO_MODEL_PATH)
        
        print(f"[INFO] SAM 모델 로딩 중: {config.SAM_MODEL_NAME}")
        # SAM 모델은 ultralytics에서 처음 실행 시 자동 다운로드됩니다.
        self.sam_model = SAM(config.SAM_MODEL_NAME)
        
        # 결과 저장 디렉토리 생성
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    def expand_bboxes(self, bboxes, img_shape, ratio=0.1):
        """
        바운딩 박스를 일정 비율만큼 확장합니다.
        :param bboxes: [x1, y1, x2, y2] 형태의 numpy array
        :param img_shape: (height, width) 이미지 크기
        :param ratio: 확장할 비율 (0.1 = 10%)
        :return: 확장된 bboxes
        """
        h, w = img_shape[:2]
        expanded_bboxes = []

        for box in bboxes:
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1

            # 확장할 픽셀 계산
            pad_x = width * ratio
            pad_y = height * ratio

            # 좌표 확장 및 이미지 경계 확인 (Clamping)
            new_x1 = max(0, x1 - pad_x)
            new_y1 = max(0, y1 - pad_y)
            new_x2 = min(w, x2 + pad_x)
            new_y2 = min(h, y2 + pad_y)

            expanded_bboxes.append([new_x1, new_y1, new_x2, new_y2])
        
        return np.array(expanded_bboxes)

    def process_image(self, image_path):
        """
        이미지 하나를 받아 감지 -> 분할 -> 배경 제거 과정을 수행합니다.
        """
        filename = os.path.basename(image_path)
        print(f"\n[INFO] 처리 시작: {filename}")

        # 1. 이미지 읽기
        original_img = cv2.imread(image_path)
        if original_img is None:
            print(f"[ERROR] 이미지를 읽을 수 없습니다: {image_path}")
            return

        # 2. YOLO로 상표 위치 감지 (Bbox Detection)
        # conf=0.5 등 설정값은 config.py에서 가져옴
        yolo_results = self.yolo_model.predict(
            original_img, 
            conf=config.CONF_THRESHOLD, 
            iou=config.IOU_THRESHOLD,
            verbose=False
        )

        # 감지된 객체가 없으면 종료
        if len(yolo_results[0].boxes) == 0:
            print("[INFO] 감지된 상표가 없습니다.")
            return

        # 감지된 모든 박스에 대해 처리
        # (한 이미지에 상표가 여러 개일 수도 있음)
        bboxes = yolo_results[0].boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2] 좌표들

        print(f"[INFO] {len(bboxes)}개의 상표가 감지되었습니다.")
        
        # 2-1. 바운딩 박스 확장 (Padding)
        # config.BBOX_EXPANSION_RATIO 만큼 박스를 키워서 SAM에게 전달
        img_h, img_w = original_img.shape[:2]
        bboxes = self.expand_bboxes(bboxes, (img_h, img_w), ratio=config.BBOX_EXPANSION_RATIO)

        # 3. SAM으로 정밀 분할 (Segmentation) 및 배경 제거
        # SAM 2 모델에 전체 이미지와 박스 정보를 줍니다.
        # Ultralytics SAM은 predict 함수에 bboxes 인자를 지원합니다.
        
        # 주의: SAM에 박스를 줄 때는 리스트 형태로 줘야 합니다.
        sam_results = self.sam_model(original_img, bboxes=bboxes, verbose=False)

        # 4. 마스크 추출 및 합성 (누끼 따기)
        # 결과 이미지 생성 (투명 배경을 위해 4채널 BGRA 생성)
        # 초기값은 완전 투명(0)
        h, w = original_img.shape[:2]
        final_result = np.zeros((h, w, 4), dtype=np.uint8)

        # 원본 이미지도 BGRA로 변환 (알파 채널 255로 불투명하게)
        img_bgra = cv2.cvtColor(original_img, cv2.COLOR_BGR2BGRA)

        # SAM 결과에서 마스크 꺼내기
        # sam_results[0].masks.data는 (N, H, W) 형태의 텐서입니다.
        if sam_results[0].masks is not None:
            masks = sam_results[0].masks.data.cpu().numpy()  # True/False 마스크

            # 여러 개의 마스크를 하나로 합침 (Logical OR 연산)
            combined_mask = np.zeros((h, w), dtype=bool)
            for mask in masks:
                # 마스크 크기가 이미지와 다를 경우 리사이즈 (가끔 발생 가능)
                if mask.shape != (h, w):
                    mask = cv2.resize(mask.astype(np.uint8), (w, h)).astype(bool)
                combined_mask = np.logical_or(combined_mask, mask)

            # 5. 마스크 적용
            # 마스크가 True인 부분만 원본 이미지 픽셀을 복사
            # final_result의 알파 채널이 0인 상태에서, 마스크 영역만 값을 채움
            final_result[combined_mask] = img_bgra[combined_mask]

            # 6. 결과 저장
            save_path = os.path.join(config.OUTPUT_DIR, f"removed_bg_{filename[:-4]}.png")
            cv2.imwrite(save_path, final_result)
            print(f"[SUCCESS] 저장 완료: {save_path}")
            
            # (옵션) 디버깅용: 박스가 그려진 원본 이미지도 저장할까요?
            # yolo_results[0].save(os.path.join(config.OUTPUT_DIR, f"bbox_{filename}"))
        else:
            print("[WARNING] 박스는 찾았으나 SAM이 마스크를 생성하지 못했습니다.")

if __name__ == "__main__":
    print("이 파일은 모듈입니다. main.py를 실행해주세요.")
