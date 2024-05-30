import os


def util_api(api_key, model, system_prompt, user_prompt):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0
    }

    return api_url, headers, data


async def call_api(api_url, headers, data):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"Error: {response.status_code}, {response.text}"


def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)
    if api_key is None:
        raise ValueError("API key is not set")
    return api_key


get_api_key()
