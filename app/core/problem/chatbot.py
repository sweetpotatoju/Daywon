# gpt_chatbot.py
import openai
from pydantic import BaseModel
from app.core.api import get_api_key

api_key = get_api_key()
model = 'gpt-4'

# OpenAI API 키 설정
openai.api_key = api_key

# GPT 프롬프트에 맥락 추가
context = """
You are a financial learning chatbot. Your job is to help users understand various financial concepts, answer questions about stocks, investments, economic indicators, and other financial topics in a clear and concise manner. Provide detailed explanations where necessary, and ensure the information is accurate and up-to-date.
"""

# 대화 기록을 저장할 변수
conversation_history = ""


class Message(BaseModel):
    message: str


def add_to_conversation(user_input: str, gpt_response: str):
    global conversation_history
    conversation_history += f"사용자: {user_input}\nGPT: {gpt_response}\n"


def ask_gpt(prompt: str) -> str:
    response = openai.Completion.create(
        engine=model,  # 최신 모델 사용
        prompt=context + prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()
