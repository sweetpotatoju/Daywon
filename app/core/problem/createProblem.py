import httpx
from fastapi import Depends, HTTPException
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트


async def create_problem(api_key, model, system_prompt, user_prompt):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("content", "")
        else:
            return f"Error: {response.status_code}, {response.text}"