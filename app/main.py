from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import re

from app.core.db import models, schemas, crud
from app.core.db.base import SessionLocal, engine
from app.core.db.crud import get_user_by_email, update_user, update_user_points, get_user, update_script, \
    update_case_script, update_question, update_comment, get_category_by_content
from app.core.db.schemas import UserCreate, UserBase, Login, UserUpdate, PointsUpdate, ModifyScriptRequest
from passlib.context import CryptContext

from app.core.problem.createProblem import create_problem, combine_problem_parts, merge_explanations, \
    modify_problem_comment
from app.core.prompt_image.createImage import generate_images
from app.core.prompt_image.createPrompt import create_prompt, create_case_prompt, modify_prompt, modify_case_prompt
from app.core.video.createVideo import VideoCreator, ftp_directory

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("admin_web", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Dependency(DB 접근 함수)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 유저 생성
# 프론트앤드에서 오류가 낫을때, 필드의 값을 대채워달라는 메시지 표시(422 Unprocessable Entity 응답일때)
@app.post("/users/", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, e_mail=user.e_mail) or crud.get_user_by_nickname(db, nickname=user.nickname):
        raise HTTPException(status_code=400, detail="Email or nickname already registered")
    return crud.create_user(db=db, user_create=user)


@app.get("/users/{user_id}/readuser", response_model=schemas.UserBase)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    return user


@app.get("/users/check_email/")
def check_email(email: str, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, e_mail=email):
        return {"is_available": False}
    return {"is_available": True}


@app.get("/users/check_nickname/")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    if crud.get_user_by_nickname(db, nickname=nickname):
        return {"is_available": False}
    return {"is_available": True}


# 사용자 정보를 검색하는 엔드포인트
@app.get("/users/{e_mail}", response_model=schemas.UserBase)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, e_mail=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login/", response_model=UserBase)
def login(credentials: Login, db: Session = Depends(get_db)):
    user = get_user_by_email(db, e_mail=credentials.e_mail)
    # 비밀번호 확인
    if not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user


@app.put("/user/{user_id}/update")
def update_user_info(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
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
def update_points(user_id: int, points_update: PointsUpdate, db: Session = Depends(get_db)):
    try:
        update_user_points(db, user_id, points_update.user_point)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "user_point": points_update.user_point,
        "message": "User points updated successfully"
    }


@app.get("/user/{user_id}/ranking")
def get_user_ranking(user_id: int, db: Session = Depends(get_db)):
    ranking = db.query(models.Ranking).filter(models.Ranking.user_id == user_id).first()
    if ranking is None:
        raise HTTPException(status_code=404, detail="Ranking not found for user")

    return {
        "user_id": ranking.user_id,
        "ranking_position": ranking.ranking_position,
        "user_point": ranking.user_point
    }


@app.post("/user_history/")
def create_user_history(user_id: int, script_id: int, T_F: bool, db: Session = Depends(get_db)):
    crud.create_user_history(db, user_id=user_id, script_id=script_id, T_F=T_F)
    return {"success"}


@app.put("/user_update_history/")
def update_user_history(user_id: int, scripts_id: int, T_F: bool, db: Session = Depends(get_db)):
    crud.update_user_history(db, user_id=user_id, script_id=scripts_id, T_F=T_F)
    return {"success"}


@app.get("/get_user_history/{user_id}")
def get_user__history(user_id: int, T_F: bool, db: Session = Depends(get_db)):
    user_history = crud.get_user_history(db, user_id=user_id, T_F=T_F)
    if not user_history:
        raise HTTPException(status_code=404, detail="User history not found")
    return user_history


#################################################

@app.get("/scripts_read/{scripts_id}")
def read_script(scripts_id: int, db: Session = Depends(get_db)):
    db_script = crud.get_script(db, scripts_id=scripts_id)
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_script


@app.post("/create_content/")
async def create_content(db: Session = Depends(get_db)):
    try:
        parts, level, category = await create_prompt("핀테크")
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

        last_file = crud.get_latest_shortform(db)
        last_file_name = last_file.form_url
        match = re.search(r'(\d+)', last_file_name)

        if not match:
            raise ValueError("Filename does not contain a number.")

        # 추출된 숫자를 +1 합니다.
        number = int(match.group(1))
        incremented_number = number + 1

        # 새로운 숫자를 포함하여 파일 이름을 생성합니다.
        new_filename = re.sub(r'\d+', str(incremented_number), last_file_name)

        clips_info = []
        await generate_images(case_script_split, clips_info)
        video_creator = VideoCreator(clips_info, ftp_directory, new_filename)
        await video_creator.create_video()
        shortform_name = new_filename

        shortform = {
            "scripts_id": script_id,
            "form_url": shortform_name
        }
        crud.create_shortform(db, shortform_data=shortform)

        combined_conceptual_script = " ".join(parts)
        combined_case_script = " ".join(case_script_split)

        problem_parts = await create_problem(combined_conceptual_script, combined_case_script, level)
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


@app.post("/modify_case_scripts/{case_scripts_id}")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
