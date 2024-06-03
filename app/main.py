from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.core.db import models, schemas, crud
from app.core.db.base import SessionLocal, engine
from app.core.db.crud import get_user_by_email, update_user, update_user_points, get_user
from app.core.db.schemas import UserCreate, UserBase, Login, UserUpdate, PointsUpdate
from passlib.context import CryptContext

from app.core.problem.createProblem import create_problem
from app.core.prompt_image.createImage import generate_images
from app.core.prompt_image.createPrompt import create_prompt, create_case_prompt
from app.core.video.createVideo import VideoCreator, ftp_directory

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


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

@app.get("/scripts_read/{scripts_id}")
def read_script(scripts_id: int, db: Session = Depends(get_db)):
    db_script = crud.get_script(db, scripts_id=scripts_id)
    if db_script is None:
        raise HTTPException(status_code=404, detail="Script not found")
    return db_script


@app.post("/create_content/")
async def create_content(db: Session = Depends(get_db)):
    try:
        parts, level, category = await create_prompt()
        conceptual_script_data = {
            "level": 1,
            "category_name": 1,  # 수정
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
        case_script = crud.create_case_script(db, case_script_data=case_script_data)

        clips_info = []
        await generate_images(case_script_split, clips_info)
        video_creator = VideoCreator(clips_info, ftp_directory)
        shortform_video = await video_creator.create_video()
        shortform_name = video_creator.get_detail_name()

        shortform = {
            "scripts_id": script_id,
            "form_url": shortform_name
        }
        shortform_content = crud.create_shortform(db, shortform_data=shortform)

        combined_conceptual_script = " ".join(parts)
        combined_case_script = " ".join(case_script_split)

        problem_parts = await create_problem(combined_conceptual_script, combined_case_script, level)
        problem_data = {
            "scripts_id": script_id,
            "plus_point": problem_parts["plus_point"],
            "minus_point": problem_parts["minus_point"],
            "question": problem_parts["문제"],
            "option_1": problem_parts["보기"][1],
            "option_2": problem_parts["보기"][2],
            "option_3": problem_parts["보기"][3],
            "option_4": problem_parts["보기"][4],
            "answer_option": problem_parts["정답"],  # 정답 번호
            "explanation": problem_parts["해설"]
        }
        problem_content = crud.create_question(db, question_data=problem_data)

        return {"message": "Content created successfully"}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
