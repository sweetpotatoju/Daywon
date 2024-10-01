from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from app.core.api import get_api_key, util_chat_api, call_api
from fastapi.responses import JSONResponse

router = APIRouter()

api_key = get_api_key()
model = 'gpt-4o'

# GPT 프롬프트에 맥락 추가
context = """
너는 한국어로만 말힐 수 있는 금융 지식에 대한 학생들의 질문을 해결해주는 챗봇이야. 또한, 너무 어려운 단어는 쓰지 않아. 특히 물어본 것에 최선을 다해 대답해줘
"""

# 대화 기록을 저장할 변수
conversation_history = [
    {"role": "system", "content": context}
]


class Message(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chatbot", response_model=ChatResponse)
async def chat(message: Message):
    user_input = message.message

    # 사용자 입력을 대화 기록에 추가
    conversation_history.append({"role": "user", "content": user_input})

    # API 호출을 위한 데이터 준비
    api_url, headers, data = util_chat_api(api_key, model, conversation_history)

    # GPT에 요청
    gpt_response = await call_api(api_url, headers, data)

    if "Error" in gpt_response:
        raise HTTPException(status_code=500, detail=gpt_response)

    # GPT 응답을 대화 기록에 추가
    conversation_history.append({"role": "assistant", "content": gpt_response})

    response_data = ChatResponse(response=gpt_response)
    return JSONResponse(content=jsonable_encoder(response_data), status_code=200)
