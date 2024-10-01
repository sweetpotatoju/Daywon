import unittest
from unittest import TestCase
from app.core.prompt_image.createPrompt import create_prompt, create_example_prompt
from app.core.problem.createProblem import create_problem

class Test(unittest.IsolatedAsyncioTestCase):
    async def test_createScript(self, finance_category=None):
        result = await create_prompt(finance_category)
        self.assertIsNotNone(result)
        print(result)

        test_example = await create_example_prompt(result)
        print(test_example)