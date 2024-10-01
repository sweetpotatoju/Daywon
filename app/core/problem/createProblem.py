import re

from app.core.api import util_api, get_api_key, call_api  # 앞서 정의한 함수를 임포트
import random

api_key = get_api_key()
model = 'gpt-4o'


def split_explanation_into_four_parts(explanation_text):
    length = len(explanation_text)
    part_length = length // 4
    explanations = []

    for i in range(3):  # 첫 3개의 파트를 추가
        start_index = i * part_length
        end_index = (i + 1) * part_length
        explanations.append(explanation_text[start_index:end_index].strip())

    explanations.append(explanation_text[3 * part_length:].strip())  # 마지막 파트를 추가
    return explanations


def parse_problem(origin_problem, level=None, plus_point=None, minus_point=None):
    problem_parts = {
        "question": None,
        "options": {},
        "answer_option": None,
        "explanation": None,
        "level": level,
        "plus_point": plus_point,
        "minus_point": minus_point,
        "explanation_1": None,
        "explanation_2": None,
        "explanation_3": None,
        "explanation_4": None
    }

    lines = origin_problem.split('\n')
    current_key = None

    for line in lines:
        line = line.strip()  # 각 라인의 앞뒤 공백 제거
        print(f"Processing line: '{line}'")  # 디버깅을 위한 출력
        if line.startswith('문제:'):
            current_key = "question"
            problem_parts[current_key] = line[len("문제:"):].strip()
            print(f"Question identified: {problem_parts[current_key]}")  # 디버깅을 위한 출력
        elif line.startswith("보기:"):
            current_key = "options"
        elif line.startswith("정답:"):
            current_key = "answer_option"
            answer_text = line[len("정답:"):].strip()
            if answer_text.endswith("번"):
                answer_text = answer_text[:-1].strip()  # "번"을 제거하고 공백 제거
            try:
                answer_number = int(re.search(r'\d+', answer_text).group())
                problem_parts[current_key] = answer_number
                print(f"Answer identified: {problem_parts[current_key]}")  # 디버깅을 위한 출력
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid answer option format: {answer_text}")
        elif line.startswith("해설:"):
            current_key = "explanation"
            explanation_text = line[len("해설:"):].strip()
            explanations = split_explanation_into_four_parts(explanation_text)
            for i, explanation in enumerate(explanations):
                if i < 4:  # 최대 4개로 제한
                    problem_parts[f"explanation_{i + 1}"] = explanation.strip()
                    print(f"Explanation part {i + 1} identified: {explanation.strip()}")  # 디버깅을 위한 출력
        elif current_key == "options":
            match = re.match(r"(\d+)\.\s*(.*)", line)
            if match:
                option_number = int(match.group(1))
                option_text = match.group(2).strip()
                problem_parts[current_key][option_number] = option_text
                print(f"Option {option_number} identified: {option_text}")  # 디버깅을 위한 출력

    return problem_parts


async def create_problem(script, example_script, level):
    system_prompt = f"""
    다음 조건을 모두 만족하는 문제를 만들어주세요.
    1 - 생성된 문제의 보기는 4개만 만들어 주세요.
    2 - 문제의 정답에 대한 설명과 오답에 대한 설명을 해설로 작성해주세요.
    3 - 문제를 생성할 때에는 한글만 사용해주세요.
    4 - 앞 뒤 문맥을 고려해서 문장들을 작성해주세요.
    5 - 명확한 정답 보기 1개와 확실한 오답 이유가 있는 오답 보기 3개로 만들어주세요.
    6 - 엔터 한번만 쳐

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
        system_prompt += "초등학교 1학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 2:
        system_prompt += "초등학교 3학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 3:
        system_prompt += "초등학교 6학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 4:
        system_prompt += "중학교 2학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    elif level == 5:
        system_prompt += "고등학교 3학년 학생들을 위한 난이도로 문제를 만들어 주세요."
    else:
        return "유효하지 않은 레벨입니다."

    user_prompt = f"""
    문제: {script}와 {example_script}에서 언급한 내용을 이용하여 객관식 문제 하나를 만들어주세요.
    문제 형식은 객관식이며, 선택지는 4 개입니다.
    문제의 정답은 확실하게 한 개만 존재해야 합니다.
    정답이 아닌 나머지 3개의 선택지는 명백히 오답이어야 합니다.
    해설: 문제의 정답과 왜 그 답이 맞는지에 대해 간단하고 이해하기 쉬운 설명을 포함해주세요.
    영어가 아닌 한글 또는 한국어로만 작성해주세요.
    """

    plus_point, minus_point = generate_random_points(level)
    api_url, headers, data = util_api(api_key, model, system_prompt, user_prompt)
    origin_problem = await call_api(api_url, headers, data)
    print(origin_problem)
    problem_parts = parse_problem(origin_problem, level, plus_point, minus_point)
    print(problem_parts)

    return problem_parts


def generate_random_points(level):
    if level == 1:
        plus_point = random.randint(1, 5)
        minus_point = random.randint(-5, -1)
    elif level == 2:
        plus_point = random.randint(1, 10)
        minus_point = random.randint(-10, -1)
    elif level == 3:
        plus_point = random.randint(1, 20)
        minus_point = random.randint(-20, -1)
    elif level == 4:
        plus_point = random.randint(1, 30)
        minus_point = random.randint(-30, -1)
    elif level == 5:
        plus_point = random.randint(1, 50)
        minus_point = random.randint(-50, -1)
    else:
        raise ValueError("레벨은 1에서 5 사이여야 합니다")

    return plus_point, minus_point


async def modify_problem_comment(original_problem, new_prompt):
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
    print(modify_problem_data)

    # 수정된 문제 파싱
    problem_parts = parse_problem(modify_problem_data)

    return problem_parts


def combine_problem_parts(problem_parts, comment):
    combined_dict = {}
    if problem_parts:
        combined_dict = {
            "문제": problem_parts.question if problem_parts.question is not None else "",
            "보기": {
                1: problem_parts.option_1 if problem_parts.option_1 is not None else "",
                2: problem_parts.option_2 if problem_parts.option_2 is not None else "",
                3: problem_parts.option_3 if problem_parts.option_3 is not None else "",
                4: problem_parts.option_4 if problem_parts.option_4 is not None else "",
            },
            "정답": problem_parts.answer_option if problem_parts.answer_option is not None else 0,
            "explanation": comment if comment is not None else ""
        }
    else:
        combined_dict = {
            "문제": "",
            "보기": {
                1: "",
                2: "",
                3: "",
                4: "",
            },
            "정답": 0,
            "explanation":  ""
        }

    return combined_dict


def merge_explanations(comment):
    explanations = [
        getattr(comment, "comment_1", ""),
        getattr(comment, "comment_2", ""),
        getattr(comment, "comment_3", ""),
        getattr(comment, "comment_4", "")
    ]
    merged_explanation = " ".join(filter(None, explanations))
    return merged_explanation
