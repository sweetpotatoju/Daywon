import unittest
from unittest import TestCase
from app.core.prompt_image.createPrompt import create_prompt, create_example_prompt
from app.core.problem.createProblem import create_problem
from app.core.prompt_image.createImage import generate_images
from app.core.prompt_image.createPrompt import split_text, split_text_two


class Test(unittest.IsolatedAsyncioTestCase):
    async def test_createPrompts(self,finance_category=None):

        result = await create_prompt(finance_category)
        self.assertIsNotNone(result)
        print(f"\n생성된 개념 스크립트\n\n {result}")

        example = await create_example_prompt(result)
        print(f"\n생성된 예시 스크립트\n\n {example}")

        problem = await create_problem(result, example)
        print(f"\n생성된 문제\n\n {problem}")

        # scripts = split_text(example)
        # scripts = split_text_two(example)
        # print(scripts)
        #
        # clips_info = []
        # makeImg = await generate_images(scripts, clips_info)
        # print(clips_info)