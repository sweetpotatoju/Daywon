import httpx
import random

import requests
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key
import openai
import webbrowser
import urllib.request


async def call_api(api_url, headers, data):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"Error: {response.status_code}, {response.text}"


async def create_prompt(finance_category):
    api_key = get_api_key()
    model = 'gpt-4'
    system_prompt = "금융 지식을 예시를 들지 않고, 공백 포함한 글자 수를 300자 이내로 요약하여 고등학생에게 이야기를 들려주듯이 쉽게 알려줍니다."
    user_prompt = f"{get_finance_category(finance_category)}를 주제로 정하고, 주제의 금융 상품 중 하나에 대한 설명과 장단점 알려줘."
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    return await call_api(api_url, headers, data)


async def create_video_prompt(conceptual_prompt):
    api_key = get_api_key()
    model = 'gpt-4'
    system_prompt = f"각 문장의 글자 수가 80자 이내인 총 6문장으로 설명하고, 어린 아이에게 이야기하는 느낌으로 말한다. 온점은 오로지 문장이 끝났을 때만 사용합니다."
    user_prompt = f"{conceptual_prompt}에 대한 구체적인 실생활 예시를 들고 알아 듣기 쉽게 설명해줘"
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    return await call_api(api_url, headers, data)


def get_finance_category(finance_category=None):
    finance_categories = {'저축', '투자', '세금'}
    if finance_category is None:
        finance_category = random.choice(list(finance_categories))
    return finance_category


def get_finance_level(finance_level=None):
    # 예시
    finance_levels = {0, 1, 2, 3, 4}
    if finance_level is None:
        finance_level = random.choice(list(finance_levels))
    return finance_level


# 2 문장씩 분리
def split_text_two(text):
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


def split_text(text):
    # 문장을 온점(.) 기준으로 나누기
    sentences = text.split('.')

    # 결과가 빈 문자열이 아닌 경우에만 리스트에 추가
    sentences = [sentence.strip() + '.' for sentence in sentences if sentence.strip()]
    return sentences
