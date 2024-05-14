import unittest
from unittest import TestCase
from app.core.prompt_image.createPrompt import create_prompt
from app.core.problem.createProblem import create_problem

class Test(unittest.IsolatedAsyncioTestCase):
    async def test_createScript(self, finance_category=None):
        result = await create_prompt(finance_category)
        self.assertIsNotNone(result)
        print(result)

        test_problem = await create_problem(result)
        print(test_problem)