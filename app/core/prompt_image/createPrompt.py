import httpx
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key
import openai
import webbrowser
import urllib.request
import os


async def create_prompt(api_key):
    model = 'gpt-4'
    system_prompt = "금융 상품을 고르는 상황 예시를 들어서 어려운 금융 지식을 각 문장의 글자 수가 50자 이내인 총 6문장으로 요약하여 고등학생에게 이야기를 들려주듯이 알려줍니다."
    user_prompt = "투자, 세금, 저축 중 하나만 골라 주제를 정하고, 그 주제에 관한 구체적 상품 예시 하나를 들고 설명과 장단점 알려줘."
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"


async def generate_images(prompt_p, api_key_p, clips_info_p):
    client = openai.OpenAI(api_key=api_key_p)

    # 각 프롬프트에 대해 이미지 생성 요청
    for i, prompt in enumerate(prompt_p):
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
        clips_info_p.append((img_dest, prompt))


# 2 문장씩 분리
def text_split(text):
    # 문장을 온점(.) 기준으로 나누기
    sentences = text.split('.')

    # 결과가 빈 문자 열이 아닌 경우 에만 리스트에 추가
    sentences = [sentence.strip() + '.' for sentence in sentences if sentence.strip()]
    sentence_pairs = []

    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences):
            sentence_pairs.append(sentences[i] + " " + sentences[i + 1])
        else:
            sentence_pairs.append(sentences[i])
    return sentence_pairs


def create_image_file_name():
    """저장할 이미지 파일의 이름을 중복되지 않게 생성"""
    count = 1
    while True:
        image_path = f"./ai_image/ai_image_result_{count}.jpg"
        if not os.path.exists(image_path):
            return image_path
        count += 1


def ensure_folders_exists(self):
    # ai_image 폴더가 있는지 확인하고 없다면 생성
    os.makedirs('./ai_image', exist_ok=True)
