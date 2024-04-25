import httpx
from fastapi import Depends,HTTPException
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트


async def create_problem_endpoint(api_key: str = Depends(get_api_key)):
    model = "gpt-4"
    system_prompt = "금융 상품을 고르는 상황 예시를 들어서 어려운 금융 지식을 각 문장의 글자 수가 50자 이내인 총 6문장으로 요약하여 고등학생에게 이야기를 들려주듯이 알려줍니다."
    user_prompt = "투자, 세금, 저축 중 하나만 골라 주제를 정하고, 그 주제에 관한 구체적 상품 예시 하나를 들고 설명과 장단점 알려줘."

    api_url, headers, data = util_api(model, system_prompt, user_prompt)  # Adjust this call if needed

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        response_data = response.json()
        problem_content = response_data.get("choices", [{}])[0].get("content", "")
        return {"problem": problem_content}