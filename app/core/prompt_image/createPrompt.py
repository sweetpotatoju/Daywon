import httpx
import random
from app.core.api import util_api, get_api_key


async def call_api(api_url, headers, data):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"Error: {response.status_code}, {response.text}"


async def create_prompt(finance_category):
    api_key = get_api_key()
    model = 'gpt-4'

    level = get_finance_level()
    print(level)

    if level == 1:
        system_prompt = """
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 금융 지식에 대한 개념만 설명해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 금융 개념과 용어에 익숙하지 않은 사람들에게 이야기 하듯이 작성해주세요.
        """

    elif level == 2:
        system_prompt = """
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 금융 지식에 대한 개념만 설명해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 -  문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 용어는 알고 있지만, 금융 상품과 서비스에 대한 이해가 제한적인 사람들에게 이야기 하듯이 작성해주세요.
        """

    elif level == 3:
        system_prompt = """
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 금융 지식에 대한 개념만 설명해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 -  문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 상품과 서비스를 이해하고 있으며, 다양한 투자 옵션에 대한 지식을 확장하고 싶어하는 사람들에게 이야기 하듯이 작성해주세요.
        """

    elif level == 4:
        system_prompt = """
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 금융 지식에 대한 개념만 설명해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 -  문장들의 앞 뒤 문맥을 고려해서, 다양한 투자 상품에 대한 좋은 이해를 가지고 있고, 복잡한 금융 전략과 시장 분석에 대한 지식을 더욱 깊이 있게 이해하고자 하는 사람들에게 이야기 하듯이 작성해주세요.
        """

    elif level == 5:
        system_prompt = """
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 금융 지식에 대한 개념만 설명해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 -  문장들의 앞 뒤 문맥을 고려해서, 금융 분야에서 근무하거나 고급 금융 이론과 실무 경험을 갖춘 사람들에게 이야기 하듯이 작성해주세요.
        """
    else:
        return "Invalid level"

    # system_prompt = "금융 지식을 예시를 들지 않고, 공백 포함한 글자 수를 300자 이내로 요약하여 고등학생에게 이야기를 들려주듯이 쉽게 알려줍니다."
    user_prompt = f"""
    다음 동작을 수행하세요.
    1 - {get_finance_category(finance_category)}를 주제로 정하세요.
    2 - 정해진 주제의 금융 상품 중 하나에 대한 개념을 설명해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    return await call_api(api_url, headers, data)


async def create_example_prompt(conceptual_prompt):
    api_key = get_api_key()
    model = 'gpt-4'
    system_prompt = """
    다음 조건들을 모두 만족하는 문장을 만들어주세요.
    1 - 각 문장의 글자 수가 80자 이내로 총 6개의 문장을 작성해주세요.
    2 - 영어가 아닌 한글만 사용해주세요.
    3 - 10대에게 이야기하듯이 작성해주세요.
    4 - 온점은 오로지 문장이 끝났을 때만 사용해주세요.
    """

    user_prompt = f"""
    다음 동작을 수행하세요. 
    1 -{conceptual_prompt}에 대한 구체적인 실생활 예시를 들어주세요. 
    2 -10대에게 이야기하듯이 알아 듣기 쉽게 작성해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    return await call_api(api_url, headers, data)


def get_finance_category(finance_category=None):
    finance_categories = {'저축', '투자', '세금'}
    if finance_category is None:
        finance_category = random.choice(list(finance_categories))
    return finance_category


def get_finance_level(finance_level=None):
    # 예시
    finance_levels = {1, 2, 3, 4, 5}
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
