import httpx
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key
import openai
import webbrowser
import urllib.request
import os


async def generate_images(prompt, clips_info):
    api_key = get_api_key()
    client = openai.OpenAI(api_key=api_key)

    # 각 프롬프트에 대해 이미지 생성 요청
    for i, prompt in enumerate(prompt):
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="standard"
        )
        # 생성된 이미지 url 열기
        url = response.data[0].url
        webbrowser.open(url)

        # 생성된 이미지 저장
        img_dest = create_image_file_name()

        urllib.request.urlretrieve(url, img_dest)
        clips_info.append((img_dest, prompt))


def create_image_file_name():
    """저장할 이미지 파일의 이름을 중복되지 않게 생성"""
    # 폴더 확인 및 생성
    os.makedirs('./ai_image', exist_ok=True)

    count = 1
    while True:
        image_path = f"./ai_image/ai_image_result_{count}.jpg"
        if not os.path.exists(image_path):
            return image_path
        count += 1
