import asyncio

from app.core.problem.createProblem import create_problem

# 새로운 스크립트와 예시 스크립트, 난이도
script = "저축은 돈을 절약하여 미래에 사용할 수 있도록 하는 것입니다."
example_script = "매달 1만원을 저축하면 1년 후에는 12만원을 모을 수 있습니다. 이는 1만원을 12번 저축했기 때문입니다."
level = 1


async def test_create_problem():
    problem = await create_problem(script, example_script, level)
    print(problem)


# 비동기 함수 호출
asyncio.run(test_create_problem())
