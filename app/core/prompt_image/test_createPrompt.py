import unittest
from unittest import TestCase
from app.core.prompt_image.createPrompt import create_prompt, create_video_prompt
from app.core.problem.createProblem import create_problem
from app.core.prompt_image.createImage import generate_images
from app.core.prompt_image.createPrompt import split_text


class Test(unittest.IsolatedAsyncioTestCase):
    async def test_create_video_prompt(self,finance_category=None):

        result = await create_prompt(finance_category)
        self.assertIsNotNone(result)
        print(f"생성된 개념 스크립트 : {result}")

        example = await create_video_prompt(result)
        print(f"생성된 예시 스크립트 : {example}")

        problem = await create_problem(result, example)
        print(f"생성된 문제 : {problem}")

        scripts = split_text(example)
        print(scripts)

        clips_info = []
        makeImg = await generate_images(scripts, clips_info)

        print(clips_info)