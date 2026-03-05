# Azure Computer Vision 브랜드 감지 테스트

이 코드는 Azure Computer Vision (v3.2) API를 사용하여 이미지 내의 로고/브랜드를 감지합니다.

## 사전 준비 (Azure 설정)

1. [Azure Portal](https://portal.azure.com)에 로그인합니다.
2. **리소스 만들기**를 클릭하고 **Computer Vision** (또는 Azure AI Services)을 검색하여 생성합니다.
3. 생성된 리소스의 **개요(Overview)** 또는 **키 및 엔드포인트(Keys and Endpoint)** 페이지로 이동합니다.
4. **키 1 (Key 1)** 과 **엔드포인트 (Endpoint)** 값을 복사해 둡니다.

## 설치 방법

필요한 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

## 설정 (.env 파일)

`.env` 파일을 열고 복사해둔 키와 엔드포인트를 입력합니다.

```ini
VISION_KEY=여기에_키를_붙여넣으세요
VISION_ENDPOINT=여기에_엔드포인트를_붙여넣으세요
```
(예: `VISION_ENDPOINT=https://my-vision-resource.cognitiveservices.azure.com/`)

## 실행 방법

1. 테스트할 이미지(예: `test.jpg`)를 이 폴더에 넣습니다.
2. 아래 명령어로 실행합니다.

```bash
python detect_brands.py
```

3. 실행 후 결과:
   - 콘솔에 감지된 브랜드 이름과 신뢰도(Confidence)가 출력됩니다.
   - 원본 이미지에 빨간 박스가 그려진 `detected_brands.jpg` 파일이 생성됩니다.
