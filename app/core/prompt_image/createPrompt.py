import httpx
import random
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key
import openai
import webbrowser
import urllib.request


async def create_prompt(finance_category):
    api_key = get_api_key()
    model = 'gpt-4'
    system_prompt = (f" {get_finance_category(finance_category)} 금융 상품을 고르는 상황 예시를 들어서 어려운 금융 지식을 각 문장의 글자 수가 50자 이내인 총 6문장으로 요약하여 "
                     f"고등학생에게 이야기를 들려주듯이 알려줍니다.")
    user_prompt = f"{get_finance_category(finance_category)}로 주제를 정하고, 그 주제에 관한 구체적 상품 예시 하나를 들고 설명과 장단점 알려줘."
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"


def get_finance_category(finance_category=None):
    finance_categories = {'저축', '주식', '세금'}
    if finance_category is None:
        finance_category = random.choice(list(finance_categories))
    return finance_category


# 2 문장씩 분리
def split_text(text):
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
