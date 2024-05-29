import httpx
import random
from app.core.api import util_api, get_api_key, call_api

api_key = get_api_key()
model = 'gpt-4'


async def create_prompt():
    level = get_finance_level()
    category = get_finance_category(level)

    print(level)
    print(category)

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

    user_prompt = f"""
    다음 동작을 수행하세요.
    1 - {category}를 주제로 정하세요.
    2 - 정해진 주제의 금융 상품 중 하나에 대한 개념을 설명해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)

    # return await call_api(api_url, headers, data)

    conceptual_script = await call_api(api_url, headers, data)
    return conceptual_script, level, category


async def modify_prompt(original_conceptual_script, level, category, new_prompt):
    if level == 1:
        modify_system_prompt = f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 위 스크립트를 기반으로 수정해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 금융 개념과 용어에 익숙하지 않은 사람들에게 이야기 하듯이 작성해주세요.

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
        """
    elif level == 2:
        modify_system_prompt = f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 위 스크립트를 기반으로 수정해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 용어는 알고 있지만, 금융 상품과 서비스에 대한 이해가 제한적인 사람들에게 이야기 하듯이 작성해주세요.

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
        """
    elif level == 3:
        modify_system_prompt = f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 위 스크립트를 기반으로 수정해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 기본적인 금융 상품과 서비스를 이해하고 있으며, 다양한 투자 옵션에 대한 지식을 확장하고 싶어하는 사람들에게 이야기 하듯이 작성해주세요.

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
        """
    elif level == 4:
        modify_system_prompt = f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 위 스크립트를 기반으로 수정해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 다양한 투자 상품에 대한 좋은 이해를 가지고 있고, 복잡한 금융 전략과 시장 분석에 대한 지식을 더욱 깊이 있게 이해하고자 하는 사람들에게 이야기 하듯이 작성해주세요.

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
        """
    elif level == 5:
        modify_system_prompt = f"""
        다음 조건들을 모두 만족하는 문장을 만들어주세요.
        1 - 위 스크립트를 기반으로 수정해주세요.
        2 - 공백을 포함한 글자 수를 300자 이내로 작성해주세요.
        3 - 영어가 아닌 한글만 사용해주세요.
        4 - 문장들의 앞 뒤 문맥을 고려해서, 금융 분야에서 근무하거나 고급 금융 이론과 실무 경험을 갖춘 사람들에게 이야기 하듯이 작성해주세요.

        기존 개념 적용 스크립트:
        {original_conceptual_script}

        사용자 수정 사항:
        {new_prompt}
        """
    else:
        return "Invalid level"

    modify_user_prompt = f"""
    다음 동작을 수행하세요.
    1 - 이전에 생성된 스크립트를 기반으로 {category}에 대한 내용을 추가적으로 설명하거나 수정해주세요.
    2 - 사용자 수정사항을 기반으로 수정해주세요.
    """

    modify_api_url, modify_headers, modify_data = util_api(api_key, model, modify_system_prompt, modify_user_prompt)
    modified_script = await call_api(modify_api_url, modify_headers, modify_data)

    return modified_script


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
    1 -{finance_category}에 대한 구체적인 실생활 예시를 들어주세요. 
    2 -10대에게 이야기하듯이 알아 듣기 쉽게 작성해주세요.
    """

    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    return await call_api(api_url, headers, data)


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
    return modify_case_script


def get_finance_category(level=None):
    finance_categories = {}

    if level is None:
        raise ValueError("Invalid level")
    elif (level == 1):
        finance_categories = {'저축', '계좌', '예금', '적금', '이자', '비상금', '돈', '통장', '잔액', '금리', '예산', '지출', '저축의 중요성', '신용카드',
                              '체크카드', '재무 목표 설정', '간단한 예산 관리'}
    elif (level == 2):
        finance_categories = {'신용대출', '주택담보대출', '이자율', '원리금 상환', '생명 보험', '건강 보험', '자동차 보험', '소득세', '부가가치세(VAT)',
                              '국민연금', '퇴직연금', '주식의 개념', '간단한 펀드'}
    elif (level == 3):
        finance_categories = {'주식', '채권', '펀드', '부동산', 'ETF(상장지수펀드)', '대출 상환 전략', '신용 점수 관리', '재산 보험', '보험료 계산',
                              '리스크 관리', '세금 신고', '세금 공제', '세금 환급', '개인연금', '연금 저축'}
    elif (level == 4):
        finance_categories = {'자산 배분', '위험 관리', '수익률 분석', '재무제표 분석', '손익계산서', '대차대조표', '자본 구조', '기업 재무', '기업 가치 평가',
                              '환율', '외환 거래', '해외 투자'}
    elif (level == 5):
        finance_categories = {'M&A (인수합병)', '벤처 캐피탈', '사모펀드 재무 비율 분석', '현금 흐름 분석', '자본 비용 상속세', '증여세', '고급 세금 계획',
                              '블록체인', '암호화폐', '디지털 뱅킹', '금융 기술 혁신'}

    finance_category = random.choice(list(finance_categories))
    return finance_category


def get_finance_level(finance_level=None):
    # 예시
    finance_levels = {1, 2, 3, 4, 5}
    if finance_level is None:
        finance_level = random.choice(list(finance_levels))
    return finance_level


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
