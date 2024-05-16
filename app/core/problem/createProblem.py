import httpx
from app.core.api import util_api, get_api_key  # 앞서 정의한 함수를 임포트


async def create_problem(script, example_script):
    api_key = get_api_key()
    # model = 'ft:gpt-3.5-turbo-0125:personal:daywon123:9HulgDod'
    model = 'gpt-4'

    system_prompt = f"""
    다음 조건을 모두 만족하는 문제를 만들어주세요.
    1 - Please write in a way that a teenager can understand.
    2 - Please provide only 4 options for the created problem.
    3 - Please also write an explanation for the correct answer.
    4 - Please use Korean only.
    5 - Please write taking into account the context before and after the sentences.
    6 - Please write the answer so that it contains one clearly correct answer and the rest are clearly incorrect. Any answer that is not correct must be incorrect.
    7 - If English is included, please translate it into Korean.

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

    user_prompt = f"""
    문제: {script}와 {example_script}에서 언급한 내용을 이용하여 객관식 문제 하나를 만들어주세요.
    문제 형식은 객관식이며, 선택지는 4 개입니다.
    문제의 정답은 확실하게 한 개만 존재해야 합니다.
    정답이 아닌 나머지 3개의 선택지는 명백히 오답이어야 합니다.
    해설: 문제의 정답과 왜 그 답이 맞는지에 대해 간단하고 이해하기 쉬운 설명을 포함해주세요.
    영어가 아닌 한글 또는 한국어로만 작성해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"에러: {response.status_code}, {response.text}"
