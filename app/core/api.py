import os

from app.core.problem.createProblem import create_problem
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel


def util_api(api_key, model, system_prompt, user_prompt):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    return api_url, headers, data


def get_api_key():
    return os.environ.get("OPENAI_API_KEY", "your_api_key_here")
