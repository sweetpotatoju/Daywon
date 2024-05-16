from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.core.db import models, schemas, crud
from app.core.db.base import SessionLocal, engine
from app.core.db.crud import get_user_by_email, update_user
from app.core.db.schemas import UserCreate, UserBase, Login, UserUpdate
from passlib.context import CryptContext

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


@app.put("/user/{user_id}")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
