import httpx
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트


async def create_problem(api_key):
    model='ft:gpt-3.5-turbo-0125:personal:daywon123:9HulgDod'
    system_prompt = "초등학교 수준의 객관식 문제를 출제하고 해설을 제공하는 시스템이야"
    user_prompt = (f"금융에 대한 문제를 1개 제출할꺼야 "
                   f"문제 형식은 객관식이고, 총 객관식 보기는 총  4개야. "
                   f"객관식 형태로 문제를 제출하고 문제에 대한 해설을 아래와같은 형식으로 만들어줘"
                   "문제:  해설: ")
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"