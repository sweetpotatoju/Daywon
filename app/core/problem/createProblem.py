from app.core.api import util_api, get_api_key, call_api  # 앞서 정의한 함수를 임포트


async def create_problem(script, example_script, level, custom_prompt=None):

    api_key = get_api_key()
    model = 'gpt-4'

    system_prompt = f"""
    다음 조건을 모두 만족하는 문제를 만들어주세요.
    1 - 생성된 문제의 보기는 4개만 만들어 주세요.
    2 - 문제의 정답에 대한 설명과 오답에 대한 설명을 해설로 작성해주세요.
    3 - 문제를 생성할 때에는 한글만 사용해주세요.
    4 - 앞 뒤 문맥을 고려해서 문장들을 작성해주세요.
    5 - 명확한 정답 보기 1개와 확실한 오답이유가 있는 오답 보기 3개로 만들어주세요.

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

    if level is None:
        return "레벨을 읽어 오는 중 오류가 발생했습니다."
    if level == 1:
        system_prompt = system_prompt + "초등학교 1학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 2:
        system_prompt = system_prompt + "초등학교 3학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 3:
        system_prompt = system_prompt + "초등학교 6학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 4:
        system_prompt = system_prompt + "중학교 2학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 5:
        system_prompt = system_prompt + "고등학교 3학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    else:
        return "유효하지 않은 레벨입니다."

    if custom_prompt:
        user_prompt = custom_prompt
    else:
        user_prompt = f"""

        문제: {script}와 {example_script}에서 언급한 내용을 이용하여 객관식 문제 하나를 만들어주세요.
        문제 형식은 객관식이며, 선택지는 4 개입니다.
        문제의 정답은 확실하게 한 개만 존재해야 합니다.
        정답이 아닌 나머지 3개의 선택지는 명백히 오답이어야 합니다.
        해설: 문제의 정답과 왜 그 답이 맞는지에 대해 간단하고 이해하기 쉬운 설명을 포함해주세요.
        영어가 아닌 한글 또는 한국어로만 작성해주세요.
        """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    origin_problem = await call_api(api_url, headers, data)
    return origin_problem


async def modify_problem(original_problem, new_prompt):
    api_key = get_api_key()
    model = 'gpt-4'

    system_prompt = f"""
    기존 문제를 다음과 같이 수정해 주세요.
    1. 사용자 입력을 반영하여 문제의 일부분을 수정합니다.
    2. 원래의 문제 형식과 일관성을 유지합니다.
    3. 한국어로 작성해주세요.

    원래 문제:
    {original_problem}

    사용자 수정 사항:
    {new_prompt}

    수정된 문제를 아래 형식으로 작성해주세요:
    문제:
    보기:
    1.
    2.
    3.
    4.
    정답:
    해설:
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, new_prompt)
    modify_problem_data = await call_api(api_url, headers, data)
    return modify_problem_data
