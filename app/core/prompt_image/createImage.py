from pathlib import Path
from app.core.api import  get_api_key
import openai
import webbrowser
import urllib.request
import os


async def generate_images(prompt, clips_info):
    api_key = get_api_key()
    client = openai.OpenAI(api_key=api_key)
    print(prompt)

    # 각 프롬프트에 대해 이미지 생성 요청
    for i, prompt in enumerate(prompt):
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt + "(No english text in the image. 10살 어린아이가 시청하는 만화처럼 그려줘.)",
            size="1024x1792",
            quality="standard"
        )
        # 생성된 이미지 url 열기
        url = response.data[0].url

        # 생성된 이미지 저장
        img_dest = create_image_file_name()

        urllib.request.urlretrieve(url, img_dest)
        clips_info.append((img_dest, prompt))


def create_image_file_name():
    """저장할 이미지 파일의 이름을 중복되지 않게 생성"""
    # 폴더 확인 및 생성
    #os.makedirs('./ai_image', exist_ok=True)
    image_path = Path(__file__).parent / "ai_image"
    if os.path.exists(image_path):
        print("이미지 경로 있음: ", image_path)
    image_path.mkdir(parents=True, exist_ok=True)

    count = 1
    while True:
        image_path = Path(__file__).parent / f"ai_image/ai_image_result_{count}.jpg"
        image_path_str = str(image_path)
        # 파일 저장 경로에 해당하는 디렉토리가 없는 경우 생성
        if not os.path.exists(image_path):
            return image_path_str
        count += 1
