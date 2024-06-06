import httpx
import random
from app.core.api import util_api, get_api_key, call_api

api_key = get_api_key()
model = 'gpt-4'


async def create_prompt(category,level):

    system_prompt = """
    다음 조건들을 모두 만족하는 예시 문장을 만들어주세요.
    1 - 각 문장의 글자 수가 80자 이내로 총 6개의 문장을 작성해주세요.
    2 - 영어가 아닌 한글만 사용해주세요.
    3 - 온점은 오로지 문장이 끝났을 때만 사용해주세요.
    4 - 문장들을 숫자로 구분하지 말고, 이어지게 문장들만 출력해주세요.
    5 - 문장들의 앞 뒤 문맥을 고려해서, 문장의 내용을 {} 학생들이 겪을 만한 실제 상황을 예시에 포함해주세요.
    6 - 이 연령대의 학생들이 쉽게 이해할 수 있도록 간단한 용어를 사용하고, 재미있고 친근한 예시를 포함하세요.
    7 - 대상을 언급하지 마세요.
    """

    if level == 1:
        system_prompt = system_prompt.format("초등학교 저학년")
    elif level == 2:
        system_prompt = system_prompt.format("초등학교 고학년")
    elif level == 3:
        system_prompt = system_prompt.format("중학교")
    elif level == 4:
        system_prompt = system_prompt.format("고등학교")
    elif level == 5:
        system_prompt = system_prompt.format("대학생")
    else:
        return "Invalid level"

    user_prompt = f"""
    다음 동작을 수행하세요.
    1 - {category}에 대해서 명확하게 설명해주세요. 
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    # return await call_api(api_url, headers, data)

    conceptual_script_data = await call_api(api_url, headers, data)
    conceptual_script = split_script_by_length(conceptual_script_data)
    return conceptual_script, level, category


def get_modify_system_prompt(level, original_conceptual_script, new_prompt):
    conditions = [
        "1 - 위 스크립트를 기반으로 수정해주세요.",
        "2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.",
        "3 - 영어가 아닌 한글만 사용해주세요.",

    ]

    if level == 1:
        conditions.append("4 - 문장들의 앞 뒤 문맥을 고려해서, 금융 개념과 용어에 익숙하지 않은 사람들에게 이야기 하듯이 작성해주세요.")
    elif level == 2:
        conditions.append("4 - 문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 용어는 알고 있지만, 금융 상품과 서비스에 대한 이해가 제한적인 사람들에게 이야기 하듯이 작성해주세요.")
    elif level == 3:
        conditions.append(
            "4 - 문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 상품과 서비스를 이해하고 있으며, 다양한 투자 옵션에 대한 지식을 확장하고 싶어하는 사람들에게 이야기 하듯이 작성해주세요.")
    elif level == 4:
        conditions.append(
            "4 - 문장들의 앞 뒤 문맥을 고려해서, 다양한 투자 상품에 대한 좋은 이해를 가지고 있고, 복잡한 금융 전략과 시장 분석에 대한 지식을 더욱 깊이 있게 이해하고자 하는 사람들에게 이야기 하듯이 작성해주세요.")
    elif level == 5:
        conditions.append("4 - 문장들의 앞 뒤 문맥을 고려해서, 금융 분야에서 근무하거나 고급 금융 이론과 실무 경험을 갖춘 사람들에게 이야기 하듯이 작성해주세요.")
    else:
        return "Invalid level"

    conditions_str = "\n".join(conditions)
    return f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        {conditions_str}

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
    """


async def modify_prompt(original_conceptual_script, level, category, new_prompt):
    modify_system_prompt = get_modify_system_prompt(level, original_conceptual_script, new_prompt)

    if modify_system_prompt == "Invalid level":
        return modify_system_prompt

    modify_user_prompt = f"""
    다음 동작을 수행하세요.
    1 - 이전에 생성된 스크립트를 기반으로 {category}에 대한 내용을 추가적으로 설명하거나 수정해주세요.
    2 - 사용자 수정사항을 기반으로 수정해주세요.
    3 - 사과는 하지 않고, 수정 후 전체 결과만 설명해주세요.
    """

    modify_api_url, modify_headers, modify_data = util_api(api_key, model, modify_system_prompt, modify_user_prompt)
    modified_script = await call_api(modify_api_url, modify_headers, modify_data)
    modified_conceptual_script = split_script_by_length(modified_script)

    return modified_conceptual_script


#############################적용사례 ######################################

async def create_case_prompt(finance_category):
    system_prompt = """
    다음 조건들을 모두 만족하는 문장을 만들어주세요.
    1 - 각 문장의 글자 수가 80자 이내로 총 6개의 문장을 작성해주세요.
    2 - 영어가 아닌 한글만 사용해주세요.
    3 - 10대에게 이야기하듯이 작성해주세요.
    4 - 온점은 오로지 문장이 끝났을 때만 사용해주세요.
    5 - 문장들을 숫자로 구분하지 말고, 이어지게 문장들만 출력해주세요.
    """
    user_prompt = f"""
    다음 동작을 수행하세요. 
    1 - {finance_category}에 대한 구체적인 실생활 예시를 들어주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    case_script_data = await call_api(api_url, headers, data)
    case_script_split = split_text(case_script_data)
    return case_script_split


async def modify_case_prompt(original_case_scripts, new_prompt):
    system_prompt = f"""
    기존 개념 예시 스크립트를 다음과 같이 수정해 주세요.
    1. 사용자 입력을 반영하여 스크립트의 일부분을 수정합니다.
    2. 원래의 스크립트 형식과 일관성을 유지합니다.
    3. 한국어로 작성해주세요.

    기존 개념 적용 스크립트:
    {original_case_scripts}

    사용자 수정 사항:
    {new_prompt}

    수정된 스크립트를 아래 조건을 적용한 문장으로 작성해주세요:
    1 - 각 문장의 글자 수가 80자 이내로 총 6개의 문장을 작성해주세요.
    2 - 영어가 아닌 한글만 사용해주세요.
    3 - 10대에게 이야기하듯이 작성해주세요.
    4 - 온점은 오로지 문장이 끝났을 때만 사용해주세요.
    5 - 문장들을 숫자로 구분하지 말고, 이어지게 문장들만 출력해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, new_prompt)
    modify_case_script = await call_api(api_url, headers, data)
    modify_case_script_split = split_text(modify_case_script)
    return modify_case_script_split




# 두 문장씩 분리
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


# 한 문장 분리
def split_text(text):
    # 문장을 온점(.) 기준으로 나누기
    sentences = text.split('.')

    # 결과가 빈 문자열이 아닌 경우에만 리스트에 추가
    sentences = [sentence.strip() + '.' for sentence in sentences if sentence.strip()]
    return sentences


def split_script_by_length(script, num_parts=3):
    length = len(script)
    part_size = length // num_parts
    parts = []

    for i in range(num_parts):
        start = i * part_size
        # 마지막 부분은 나머지 문장을 모두 포함
        end = (i + 1) * part_size if i != num_parts - 1 else length
        parts.append(script[start:end].strip())

    return parts
