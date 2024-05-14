from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.core.db import models, schemas, crud
from app.core.db.base import SessionLocal, engine
from app.core.db.schemas import UserRead, UserCreate

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency(DB 접근 함수)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.UserRead)  # 응답 모델을 UserRead로 변경
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.e_mail)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user_create = user)  # 수정된 CRUD 함수를 호출


@app.get("/users/{e_mail}", response_model=schemas.UserBase)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
