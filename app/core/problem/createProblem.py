import httpx
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트

async def create_problem(script, example_script):

    api_key = get_api_key()
    model='ft:gpt-3.5-turbo-0125:personal:daywon123:9HulgDod'
    system_prompt = f"""
    다음 조건을 모두 만족하는 문제를 만들어주세요.
    1 - 10대 수준에서 이해할 수 있게 작성해주세요.
    2 - 만들어진 문제의 보기는 4개만 작성해주세요.
    3 - 정답에 대한 해설도 작성해주세요.
    4 - 영어가 아닌 한글로만 작성해주세요.
    5 - 문장들의 앞, 뒤 문맥을 고려해서 작성해주세요.
    
    다음 형식을 사용하십시오.
    문제 :
    보기 :
    1.
    2.
    3.
    4.
    정답 :
    해설 :
    
    """

    user_prompt = (f"문제: {script}와 {example_script}에서 언급한 내용을 이용하여 객관식 문제 하나를 만들어주세요. 영어가 아닌 한글로만 작성해주세요."
                   f"문제 형식은 객관식이며, 선택지는 네 개입니다. 문제의 정답은 확실하게 한 개만 존재해야 합니다. 영어가 아닌 한글로만 작성해주세요."
                   f"해설: 문제의 정답과 왜 그 답이 맞는지에 대한 간단하고 이해하기 쉬운 설명을 포함해주세요. 영어가 아닌 한글로만 작성해주세요.")

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"