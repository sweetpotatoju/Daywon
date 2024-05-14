import httpx
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트


async def create_problem():
    api_key = get_api_key()
    model='ft:gpt-3.5-turbo-0125:personal:daywon123:9HulgDod'
    system_prompt = "초등학교 수준에서 이해할 수 있는 객관식 금융 문제를 만들고, 이에 대한 해설도 제공해주세요."
    user_prompt = (f"문제: 금융에 관련된 객관식 문제 하나를 만들어주세요."
                  f"문제 형식은 객관식이며, 선택지는 네 개입니다.문제의 답은 확실한 정답은 한 개이어야 합니다. "
                  f"해설: 문제의 답과 왜 그 답이 맞는지에 대한 간단하고 이해하기 쉬운 설명을 포함해주세요.")
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"