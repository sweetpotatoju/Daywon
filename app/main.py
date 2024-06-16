import io
import uvicorn
from fastapi import HTTPException, Form, Depends
import os

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import re

from starlette.middleware.cors import CORSMiddleware

from app.core.problem.chatbot import router as chat_router
from starlette.responses import RedirectResponse, JSONResponse

from app.core.FTP_SERVER.ftp_util import read_binary_file_from_ftp, list_files, download_file_from_ftp, video_from_ftp
from app.core.db import models, schemas, crud
from app.core.db.base import SessionLocal, engine
from app.core.db.crud import get_user_by_email, update_user, update_user_points, get_user, update_script, \
    update_case_script, update_question, update_comment, get_category_by_content, get_admin_by_admin_name, \
    get_user_by_email_and_name, get_user_by_nickname_and_name
from app.core.db.models import Admin
from app.core.db.schemas import UserCreate, UserBase, Login, UserUpdate, PointsUpdate, ModifyScriptRequest, AdminCreate, \
    AdminUpdate, AdminLogin, CreateContentRequest, ScriptsRead
from passlib.context import CryptContext
from typing import List, Optional

from app.core.problem.createProblem import create_problem, combine_problem_parts, merge_explanations, \
    modify_problem_comment
from app.core.prompt_image.createImage import generate_images
from app.core.prompt_image.createPrompt import create_prompt, create_case_prompt, modify_prompt, modify_case_prompt
from app.core.video.createVideo import VideoCreator, ftp_directory
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
# from starlette.templating import Jinja2Templates
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import APIKeyCookie
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from ftplib import FTP, error_perm, error_temp, all_errors
from app.core.problem.chatbot import *

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 세션 설정을 위한 비밀 키 설정 (실제 환경에서는 환경 변수로 설정)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
security = APIKeyCookie(name="session")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 HTTP 헤더를 허용
)


# Dependency(DB 접근 함수)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Message(BaseModel):
    message: str


app.include_router(chat_router, prefix="/api")


# 세션에서 현재 사용자를 가져오는 함수 정의
async def get_current_user(request: Request):
    session = request.session
    return session.get("user")


@app.get("/admin_login", response_class=HTMLResponse)
async def admin_login_web(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/admin_account_management_page", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("admin_account_management.html", {"request": request})


@app.get("/admin_mainpage", response_class=HTMLResponse)
async def admin_mainpage(request: Request, current_user_admin: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if not current_user_admin:
        return RedirectResponse(url="/admin_login", status_code=303)
    print()
    data = await get_count_data(db)
    return templates.TemplateResponse("admin_mainpage.html",
                                      {"request": request,
                                       "current_user_admin": current_user_admin,
                                       "data": data})


@app.get("/read_create_content/")
async def read_create_content_root(request: Request):
    print("Attempting to serve create_content.html")  # 디버깅: 요청 처리 시작 출력
    return templates.TemplateResponse("create_content.html", {"request": request})


@app.get("/read_content_list")
async def read_content_list_root(request: Request):
    print("Attempting to serve create_content.html")  # 디버깅: 요청 처리 시작 출력
    return templates.TemplateResponse("content_list.html", {"request": request})


@app.get("/read_admins_list/", response_model=List[schemas.Admin])
async def read_admins(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    admins = crud.get_admins(db, skip=skip, limit=limit)
    return admins


@app.post("/create_admin/")
async def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    try:
        crud.create_admin(db, admin)
        return "success"
    except Exception as e:
        # 예외가 발생하면 에러 메시지를 반환
        return "error"


@app.put("/update_admins/{admin_id}")
async def update_admin_endpoint(admin_id: int, admin_update: schemas.AdminUpdate, db: Session = Depends(get_db)):
    db_admin = crud.update_admin(db, admin_id, admin_update)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return "success"  # 성공 시 "success" 문자열 반환


@app.get("/admins_count/", response_model=int)
async def read_admin_count(db: Session = Depends(get_db)):
    count = crud.get_admin_count(db)
    return count


@app.post("/check_admin_password/")
async def check_admin_password(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    admin_password = data['password']
    admin_id = data['adminId']

    # 관리자 비밀번호 확인 로직 구현
    if not crud.check_admin_password(db, admin_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    # 사용자 비밀번호 가져오기
    user_password = crud.get_user_password(db, admin_id)
    return {"password": user_password}


# 유저 생성
# 프론트앤드에서 오류가 낫을때, 필드의 값을 대채워달라는 메시지 표시(422 Unprocessable Entity 응답일때)
@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, e_mail=user.e_mail) or crud.get_user_by_nickname(db, nickname=user.nickname):
        raise HTTPException(status_code=400, detail="Email or nickname already registered")
    return crud.create_user(db=db, user_create=user)


@app.get("/users/{user_id}/read_user", response_model=schemas.UserBase)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    return user


@app.get("/users/check_email/")
async def check_email(email: str, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, e_mail=email):
        return {"is_available": False}
    return {"is_available": True}


@app.post("/user_find-password")
async def find_password(email: str, name: str, db: Session = Depends(get_db)):
    user = get_user_by_email_and_name(db, email, name)
    if user:
        return {"password": user.hashed_password}
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/user_find-email")
async def find_email(nickname: str, name: str, db: Session = Depends(get_db)):
    user = get_user_by_nickname_and_name(db, nickname, name)
    if user:
        return {"email": user.e_mail}
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/check_nickname/")
async def check_nickname(nickname: str, db: Session = Depends(get_db)):
    if crud.get_user_by_nickname(db, nickname=nickname):
        return {"is_available": False}
    return {"is_available": True}


# 사용자 정보를 검색하는 엔드포인트
@app.get("/users/{e_mail}", response_model=schemas.UserBase)
async def read_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, e_mail=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login/", response_model=UserBase)
async def login(credentials: Login, db: Session = Depends(get_db)):
    user = get_user_by_email(db, e_mail=credentials.e_mail)
    # 비밀번호 확인
    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user


@app.put("/user/{user_id}/update")
async def update_user_info(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data_dict = update_data.dict()
    update_user(db, user_id, update_data_dict)

    db.refresh(existing_user)

    return {
        "user_id": existing_user.user_id,
        "nickname": existing_user.nickname,
        "profile_image": existing_user.profile_image
    }


@app.put("/user/{user_id}/points")
async def update_points(user_id: int, points_update: PointsUpdate, db: Session = Depends(get_db)):
    try:
        update_user_points(db, user_id, points_update.user_point)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "user_point": points_update.user_point,
        "message": "User points updated successfully"
    }


@app.get("/user/{user_id}/ranking")
async def get_user_ranking(user_id: int, db: Session = Depends(get_db)):
    ranking = db.query(models.Ranking).filter(models.Ranking.user_id == user_id).first()
    if ranking is None:
        raise HTTPException(status_code=404, detail="Ranking not found for user")

    return {
        "user_id": ranking.user_id,
        "ranking_position": ranking.ranking_position,
        "user_point": ranking.user_point
    }


@app.post("/user_history/")
async def create_user_history(user_id: int, script_id: int, T_F: bool, db: Session = Depends(get_db)):
    crud.create_user_history(db, user_id=user_id, script_id=script_id, T_F=T_F)
    return {"success"}


@app.put("/user_update_history/")
async def update_user_history(user_id: int, scripts_id: int, T_F: bool, db: Session = Depends(get_db)):
    crud.update_user_history(db, user_id=user_id, script_id=scripts_id, T_F=T_F)
    return {"success"}


@app.get("/get_user_history/{user_id}")
async def get_user__history(user_id: int, T_F: bool, db: Session = Depends(get_db)):
    user_history = crud.get_user_history(db, user_id=user_id, T_F=T_F)
    if not user_history:
        raise HTTPException(status_code=404, detail="User history not found")
    return user_history


@app.post("/category/", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)


#################################################

@app.get("/read_content_list_status/", response_model=List[ScriptsRead])
async def read_scripts(inspection_status: bool, db: Session = Depends(get_db)):
    print(f"Fetching scripts with inspection_status={inspection_status}")
    scripts = crud.get_scripts_by_inspection_status(db, inspection_status)
    if scripts is None or len(scripts) == 0:
        print("No scripts found")
        raise HTTPException(status_code=404, detail="Scripts not found")
    print(f"Found {len(scripts)} scripts")

    result = []
    for script in scripts:
        category_label = script.categories.label if script.categories else None
        category_content = script.categories.content if script.categories else None
        # print(f"Script ID: {script.scripts_id}, Category Label: {category_label}, Category Content: {category_content}")
        if category_label == 1:
            return_value = "세금"
        elif category_label == 2:
            return_value = "재산관리"
        elif category_label == 3:
            return_value = "금융시사상식"
        else:
            return_value = None

        result.append(ScriptsRead(
            category_label=category_label,
            category_content=category_content,
            level=script.level,  # 필드명을 level로 변경
            scripts_id=script.scripts_id,
            return_value=return_value
        ))

    print(f"Result: {result}")
    return result


@app.get("/scripts_read/{scripts_id}")
async def read_script(scripts_id: int, db: Session = Depends(get_db)):
    db_script = crud.get_script(db, scripts_id=scripts_id)
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_script


@app.get("/scripts_read/{scripts_id}")
async def read_script(scripts_id: int, db: Session = Depends(get_db)):
    db_script = crud.get_script(db, scripts_id=scripts_id)
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_script


@app.post("/create_content/")
async def create_content(request: CreateContentRequest, db: Session = Depends(get_db)):
    try:
        print(request.label)
        categories_name = crud.get_random_category_content_by_label(db, request.label)
        if not categories_name:
            raise HTTPException(status_code=404, detail="Label not found")

        parts, level, category = await create_prompt(categories_name, request.level)
        found_category_id = get_category_by_content(db=db, content=category)
        category_id = found_category_id.category_id

        conceptual_script_data = {
            "level": 1,
            "category_id": category_id,  # 수정
            "content_1": parts[0],
            "content_2": parts[1],
            "content_3": parts[2],
            "inspection_status": False
        }

        script_id = crud.create_script(db=db, script_data=conceptual_script_data)
        print(script_id)
        case_script_split = await create_case_prompt(category)
        case_script_data = {
            "scripts_id": script_id,
            "content_1": case_script_split[0] if len(case_script_split) > 0 else None,
            "content_2": case_script_split[1] if len(case_script_split) > 1 else None,
            "content_3": case_script_split[2] if len(case_script_split) > 2 else None,
            "content_4": case_script_split[3] if len(case_script_split) > 3 else None,
            "content_5": case_script_split[4] if len(case_script_split) > 4 else None,
            "content_6": case_script_split[5] if len(case_script_split) > 5 else None,
        }
        crud.create_case_script(db, case_script_data=case_script_data)

        combined_conceptual_script = " ".join(parts)
        print(combined_conceptual_script)
        combined_case_script = " ".join(case_script_split)
        print(combined_case_script)

        problem_parts = await create_problem(combined_conceptual_script, combined_case_script, level)
        print(problem_parts)
        problem_data = {
            "scripts_id": script_id,
            "plus_point": problem_parts["plus_point"],
            "minus_point": problem_parts["minus_point"],
            "question": problem_parts["question"],
            "option_1": problem_parts["options"][1],
            "option_2": problem_parts["options"][2],
            "option_3": problem_parts["options"][3],
            "option_4": problem_parts["options"][4],
            "answer_option": problem_parts["answer_option"],  # 정답 번호
        }
        problem_content = crud.create_question(db, question_data=problem_data)

        comment_data = {
            'q_id': problem_content.q_id,
            'comment_1': problem_parts['explanation_1'],
            'comment_2': problem_parts['explanation_2'],
            'comment_3': problem_parts['explanation_3'],
            'comment_4': problem_parts['explanation_4']
        }

        crud.create_comment(db, comment_data=comment_data)

        last_file = crud.get_latest_shortform(db)
        new_filename = None
        if last_file:
            print("a")
            last_file_name = last_file.form_url
            print("a")
            print(last_file_name)

            # 정규식을 사용하여 숫자를 추출합니다.
            match = re.search(r'(\d+)(?=\.\w+$)', last_file_name)

            if not match:
                raise ValueError("Filename does not contain a number.")

            # 추출된 숫자를 +1 합니다.
            number = int(match.group(1))
            incremented_number = number + 1

            # 새로운 파일 이름을 생성합니다.
            new_filename = re.sub(r'(\d+)(?=\.\w+$)', str(incremented_number), last_file_name)
            print(new_filename)  # "completed_video_8.mp4"
        else:
            new_filename = None

        clips_info = []
        await generate_images(case_script_split, clips_info)
        print(new_filename)
        video_creator = VideoCreator(clips_info, ftp_directory, new_filename)
        shortform_name = video_creator.get_video_file_path()
        print(f"{shortform_name}")
        await video_creator.create_video()
        shortform = {
            "scripts_id": script_id,
            "form_url": shortform_name
        }
        crud.create_shortform(db, shortform_data=shortform)

        return {"message": "Content created successfully"}

    except Exception as e:
        return {"error": str(e)}


@app.post("/modify_concept_scripts/{scripts_id}")
async def modify_scripts(scripts_id: int, request: ModifyScriptRequest, db: Session = Depends(get_db)):
    db_script = crud.get_script(db, scripts_id=scripts_id)
    if not db_script:
        raise HTTPException(status_code=404, detail="Script not found")

    combined_script = f"{db_script.content_1} {db_script.content_2} {db_script.content_3}"

    modified_content = await modify_prompt(combined_script, db_script.level, db_script.category_id,
                                           request.new_prompt)

    update_concept_data = {
        "content_1": modified_content[0],
        "content_2": modified_content[1],
        "content_3": modified_content[2],
    }
    updated_script = crud.update_script(db, scripts_id, update_concept_data)
    if not updated_script:
        raise HTTPException(status_code=500, detail="Failed to update script")
    id = updated_script.category_id
    new_finance_category = crud.get_cotegory_name_by_category_id(db, id)

    new_case_script = await create_case_prompt(new_finance_category)
    update_case_data = {
        "content_1": new_case_script[0] if len(new_case_script) > 0 else None,
        "content_2": new_case_script[1] if len(new_case_script) > 1 else None,
        "content_3": new_case_script[2] if len(new_case_script) > 2 else None,
        "content_4": new_case_script[3] if len(new_case_script) > 3 else None,
        "content_5": new_case_script[4] if len(new_case_script) > 4 else None,
        "content_6": new_case_script[5] if len(new_case_script) > 5 else None,
    }
    updated_case_script = crud.update_case_script(db, scripts_id, update_case_data)

    clips_info = []
    await generate_images(new_case_script, clips_info)

    # 원래 비디오 저장명 찾기
    db_shortform = crud.get_shortform_by_scripts_id(db, scripts_id=scripts_id)
    video_file_name = db_shortform.form_url

    # scripts_id를 통해 얻은 비디오 저장 명으로 비디오 새로 만들고 덮어 씌우기
    video_creator = VideoCreator(clips_info, ftp_directory, video_file_name)
    await video_creator.create_video()

    new_combined_conceptual_script = " ".join(modified_content)
    new_combined_case_script = " ".join(new_case_script)

    new_problem_parts = await create_problem(new_combined_conceptual_script, new_combined_case_script, db_script.level)
    update_problem_data = {
        "question": new_problem_parts["question"],
        "option_1": new_problem_parts["options"][1],
        "option_2": new_problem_parts["options"][2],
        "option_3": new_problem_parts["options"][3],
        "option_4": new_problem_parts["options"][4],
        "answer_option": new_problem_parts["answer_option"],  # 정답 번호
    }

    result = crud.get_question_by_script_id(db, scripts_id=scripts_id)
    q_id = result.q_id if result else scripts_id

    crud.update_question(db, q_id=q_id, update_data=update_problem_data)

    comment_data = {
        'comment_1': new_problem_parts['explanation_1'],
        'comment_2': new_problem_parts['explanation_2'],
        'comment_3': new_problem_parts['explanation_3'],
        'comment_4': new_problem_parts['explanation_4']
    }

    crud.update_comment(db, q_id=q_id, update_data=comment_data)

    return {"message": "Content modify successfully"}


@app.post("/modify_case_scripts/{scripts_id}")
async def modify_case_scripts(scripts_id: int, request: ModifyScriptRequest, db: Session = Depends(get_db)):
    db_case_script = crud.get_case_scripts_by_script_id(db, scripts_id=scripts_id)
    if not db_case_script:
        raise HTTPException(status_code=404, detail="Script not found")

    combined_script = " ".join([
        db_case_script.content_1, db_case_script.content_2, db_case_script.content_3,
        db_case_script.content_4, db_case_script.content_5, db_case_script.content_6
    ])

    modified_case_script_split = await modify_case_prompt(combined_script, request.new_prompt)

    new_update_case_data = {
        "content_1": modified_case_script_split[0] if len(modified_case_script_split) > 0 else None,
        "content_2": modified_case_script_split[1] if len(modified_case_script_split) > 1 else None,
        "content_3": modified_case_script_split[2] if len(modified_case_script_split) > 2 else None,
        "content_4": modified_case_script_split[3] if len(modified_case_script_split) > 3 else None,
        "content_5": modified_case_script_split[4] if len(modified_case_script_split) > 4 else None,
        "content_6": modified_case_script_split[5] if len(modified_case_script_split) > 5 else None,
    }

    updated_case_script = crud.update_case_script(db, scripts_id, new_update_case_data)
    if not updated_case_script:
        raise HTTPException(status_code=500, detail="Failed to update case script")
    clips_info = []
    await generate_images(modified_case_script_split, clips_info)

    # 원래 비디오 저장명 찾기
    db_shortform = crud.get_shortform_by_scripts_id(db, scripts_id=scripts_id)
    video_file_name = db_shortform.form_url

    # scripts_id를 통해 얻은 비디오 저장 명으로 비디오 새로 만들고 덮어 씌우기
    video_creator = VideoCreator(clips_info, ftp_directory, video_file_name)
    await video_creator.create_video()
    db_concept_script = crud.get_script(db, scripts_id)
    case_content_list = [
        db_concept_script.content_1,
        db_concept_script.content_2,
        db_concept_script.content_3
    ]
    new_new_combined_conceptual_script = " ".join(case_content_list)
    new_combined_case_script = " ".join(modified_case_script_split)

    new_problem_parts = await create_problem(new_new_combined_conceptual_script, new_combined_case_script,
                                             db_concept_script.level)
    update_problem_data = {
        "question": new_problem_parts["question"],
        "option_1": new_problem_parts["options"][1],
        "option_2": new_problem_parts["options"][2],
        "option_3": new_problem_parts["options"][3],
        "option_4": new_problem_parts["options"][4],
        "answer_option": new_problem_parts["answer_option"],  # 정답 번호
    }
    q_id = crud.get_question_by_script_id(db, scripts_id=scripts_id).q_id
    crud.update_question(db, q_id=q_id, update_data=update_problem_data)

    comment_data = {
        'comment_1': new_problem_parts['explanation_1'],
        'comment_2': new_problem_parts['explanation_2'],
        'comment_3': new_problem_parts['explanation_3'],
        'comment_4': new_problem_parts['explanation_4']
    }

    crud.update_comment(db, q_id=q_id, update_data=comment_data)

    return {"message": "Content modify successfully"}


@app.post("/modify_problem/{scripts_id}")
async def modify_problem(scripts_id: int, request: ModifyScriptRequest, db: Session = Depends(get_db)):
    db_problem_question = crud.get_question_by_script_id(db, scripts_id=scripts_id)

    db_problem_comment = crud.get_comment_by_script_id(db, scripts_id=scripts_id)

    combine_comment = merge_explanations(db_problem_comment)

    modify_combined_problem = combine_problem_parts(db_problem_question, combine_comment)
    print(modify_combined_problem)

    modified_problem = await modify_problem_comment(modify_combined_problem, request.new_prompt)
    print(modified_problem)

    update_problem_data = {
        "question": modified_problem["question"],
        "option_1": modified_problem["options"][1],
        "option_2": modified_problem["options"][2],
        "option_3": modified_problem["options"][3],
        "option_4": modified_problem["options"][4],
        "answer_option": modified_problem["answer_option"],  # 정답 번호
    }

    update_comment_data = {
        'comment_1': modified_problem['explanation_1'],
        'comment_2': modified_problem['explanation_2'],
        'comment_3': modified_problem['explanation_3'],
        'comment_4': modified_problem['explanation_4']
    }

    updated_problem = update_question(db, db_problem_question.q_id, update_problem_data)
    updated_comment = update_comment(db, db_problem_question.q_id, update_comment_data)

    if updated_problem or updated_comment:
        return {"message": "Script updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update script")


@app.post("/update_inspection_status/{scripts_id}")
async def update_inspection_status_true(scripts_id: int, db: Session = Depends(get_db)):
    inspection_status = crud.update_inspection_status(db, scripts_id)
    print(inspection_status)
    return {"scripts_id": scripts_id, "inspection_status": inspection_status}


# admin
@app.post("/admins/read_level/{admin_name}")
async def read_admin_level(admin_name: str, db: Session = Depends(get_db)):
    admin = crud.get_admin_by_admin_name(db, admin_name)
    if not admin:
        raise HTTPException(status_code=403, detail="Admin not authorized to create a new admin")
    return {"level": admin}


@app.delete("/admins/delete/{admin_id}")
async def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    if not crud.delete_admin_if_level_3(db, admin_id):
        raise HTTPException(status_code=403, detail="Admin not authorized to delete or admin not found")
    return {"detail": "Admin deleted"}


# 로그인 처리 라우트 핸들러
@app.post("/admins/login")
async def admin_login(request: Request, admin_name: str = Form(...), password: str = Form(...),
                      db: Session = Depends(get_db)):
    admin = crud.get_active_admin_by_admin_name(db, admin_name)
    if not admin or admin.password != password:
        return {"fail"}

    session = request.session
    session["user"] = {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "qualification_level": admin.qualification_level
    }
    response = RedirectResponse(url="/admin_mainpage", status_code=303)
    return response


@app.post("/admins/login_mobile")
async def admin_login(request: Request, admin_name: str = Form(...), password: str = Form(...),
                      db: Session = Depends(get_db)):
    admin = crud.get_active_admin_by_admin_name(db, admin_name)
    if not admin or admin.password != password:
        return {"status": "fail"}

    session = request.session
    session["user"] = {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "qualification_level": admin.qualification_level
    }
    return {"status": "success"}  # 성공 시 명확한 메시지 반환


@app.post("/admins/login_mobile")
async def admin_login(request: Request, admin_name: str = Form(...), password: str = Form(...),
                      db: Session = Depends(get_db)):
    admin = crud.get_active_admin_by_admin_name(db, admin_name)
    if not admin or admin.password != password:
        return {"status": "fail"}

    session = request.session
    session["user"] = {
        "admin_id": admin.admin_id,
        "admin_name": admin.admin_name,
        "qualification_level": admin.qualification_level
    }
    return {"status": "success"}  # 성공 시 명확한 메시지 반환


@app.get("/nextpage/{content_id}", response_class=HTMLResponse)
async def content_view(request: Request, content_id: int, db: Session = Depends(get_db)):
    script_data = crud.get_script(db, content_id)
    if script_data is None:
        raise HTTPException(status_code=404, detail="Script not found")

    case_script_data = crud.get_case_scripts_by_script_id(db, content_id)
    shortform_data = crud.get_shortform_by_scripts_id(db, content_id)
    problem_data = crud.get_question_by_script_id(db, content_id)
    comment_data = crud.get_comment_by_script_id(db, content_id)

    video_url = None
    remote_file_path = ""

    if shortform_data.form_url:
        remote_video_url = shortform_data.form_url
        remote_file_path = f"/video/{remote_video_url}"

    else:
        remote_video_url = "completed_video_1.mp4"
        video_response = None

    try:
        file_contents = read_binary_file_from_ftp(remote_file_path)

        if file_contents:
            video_response = StreamingResponse(io.BytesIO(file_contents), media_type="video/mp4")
            video_url = request.url_for("stream_video", video_path=remote_video_url)
        else:
            # raise HTTPException(status_code=500, detail="Failed to retrieve video")
            video_url = None
    except Exception as e:
        # raise HTTPException(status_code=500, detail="Error retrieving video from FTP server")
        video_url = None

    return templates.TemplateResponse("content_inspection_page.html", {
        "request": request,
        "script_data": script_data,
        "case_script_data": case_script_data,
        "shortform_data": shortform_data,
        "problem_data": problem_data,
        "comment_data": comment_data,
        "video_url": video_url  # 템플릿에 비디오 스트리밍 응답을 전달합니다.
    })


@app.get("/get_stream_video/{scripts_id}")
async def get_stream_video(request: Request, scripts_id: int, db: Session = Depends(get_db)):
    script_data = crud.get_script(db, scripts_id)
    if script_data is None:
        raise HTTPException(status_code=404, detail="Script not found")

    shortform_data = crud.get_shortform_by_scripts_id(db, scripts_id)
    remote_file_path = ""

    if shortform_data.form_url:
        remote_video_url = shortform_data.form_url
        remote_file_path = f"/video/{remote_video_url}"
    else:
        remote_video_url = "completed_video_1.mp4"
        remote_file_path = None

    video_stream = await video_from_ftp(remote_file_path)
    if video_stream:
        return StreamingResponse(video_stream, media_type='video/mp4')
    else:
        return HTTPException(status_code=404, detail="Video not found")


@app.get("/read/scripts/random/")
def read_random_script(category_label: int, level: int, db: Session = Depends(get_db)):
    script = crud.get_random_script_by_category_label_and_level(db, category_label, level)
    if script is None:
        raise HTTPException(status_code=404, detail="Script not found")

    combined_content = f"{script.content_1} {script.content_2} {script.content_3}".strip()

    return JSONResponse(
        content={
            "scripts_id": script.scripts_id,
            "level": script.level,
            "category_id": script.category_id,
            "inspection_status": script.inspection_status,
            "combined_content": combined_content
        },
        media_type="application/json",
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@app.get("/scripts/{scripts_id}/shortforms")
async def read_shortforms(scripts_id: int, db: Session = Depends(get_db)):
    shortform_url = crud.get_shortforms_by_scripts_id(db, scripts_id)
    if not shortform_url:
        raise HTTPException(status_code=404, detail="Shortforms not found")
    return shortform_url


@app.get("/scripts/{scripts_id}/questions")
async def read_questions(scripts_id: int, db: Session = Depends(get_db)):
    questions = crud.get_questions_by_scripts_id(db, scripts_id)
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")
    return questions


@app.get("/questions/{q_id}/comments")
async def read_comments(q_id: int, db: Session = Depends(get_db)):
    comments = crud.get_comments_by_q_id(db, q_id)
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    return comments


@app.get("/stream_video/{video_path}")
async def stream_video(request: Request, video_path: str):
    remote_file_path = f"/video/{video_path}"
    try:
        file_contents = read_binary_file_from_ftp(remote_file_path)
        if file_contents:
            return StreamingResponse(io.BytesIO(file_contents), media_type="video/mp4")
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve video")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving video from FTP server")


@app.get("/stream_mobile_video/{video_path}")
async def stream_video(request: Request, video_path: str):
    remote_file_path = f"/videos/{video_path}.mp4"
    local_file_path = os.path.join("app", "core", "video", video_path)
    download_file_from_ftp(remote_file_path, local_file_path)

    async def iterfile():
        with open(local_file_path, mode="rb") as file:
            while chunk := file.read(1024 * 1024):  # 1MB 청크
                yield chunk

    return StreamingResponse(iterfile(), media_type="video/mp4")


@app.get("/get_all_ranking/")
async def get_all_ranking(db: Session = Depends(get_db)):
    try:
        ranking = crud.get_ranking(db)
        return ranking
    except SQLAlchemyError as e:
        # log the er    ror (you can use logging module)
        raise HTTPException(status_code=500, detail="An error occurred while fetching the ranking.")
    except Exception as e:
        # log the error (you can use logging module)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@app.get("/refresh_data/{scripts_id}")
async def refresh_data(scripts_id: int, db: Session = Depends(get_db)):
    scripts = crud.get_script(db, scripts_id)
    questions = crud.get_question_by_script_id(db, scripts_id)
    comments = crud.get_comment_by_script_id(db, scripts_id)
    case_scripts = crud.get_case_scripts_by_script_id(db, scripts_id)
    shortform = crud.get_shortform_by_scripts_id(db, scripts_id)

    return {
        "script_data": scripts,
        "problem_data": questions,
        "comment_data": comments,
        "case_script_data": case_scripts,
        "shortform": shortform
    }


@app.get("/get_count_data/")
async def get_count_data(db: Session = Depends(get_db)):
    created_problem_count = crud.get_created_problem_count(db)
    true_questions_count = crud.get_true_questions_count(db)
    user_count = crud.get_user_count(db)

    return {
        "created_problem": created_problem_count,
        "true_questions_count": true_questions_count,
        "get_user_count": user_count
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=30001)
