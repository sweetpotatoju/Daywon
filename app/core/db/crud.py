from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.core.db import models, schemas
from app.core.db.models import Scripts, Question, Shortform, Admin, History, Ranking, CaseScripts, Comment, Category
from passlib.hash import bcrypt

from app.core.db.schemas import CategoryCreate, CategoryUpdate


def create_user(db: Session, user_create: schemas.UserCreate):
    # 평문 패스워드를 bcrypt 해시로 변환
    hashed_password = bcrypt.hash(user_create.hashed_password)

    # User 모델 인스턴스 생성
    user = models.User(
        name=user_create.name,
        nickname=user_create.nickname,
        e_mail=user_create.e_mail,
        level=user_create.level,
        user_point=user_create.user_point,
        hashed_password=hashed_password,  # 해싱된 비밀번호 저장
        profile_image=user_create.profile_image

    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, e_mail: str) -> object:
    return db.query(models.User).filter(models.User.e_mail == e_mail).first()


# 닉네임 중복 검사 함수

def get_user_by_nickname(db: Session, nickname: str):
    return db.query(models.User).filter(models.User.nickname == nickname).first()


def update_user(db: Session, user_id: int, update_data: dict):
    # 사용자 정보 갱신 (닉네임과 프로필 이미지만)
    db.query(models.User).filter(models.User.user_id == user_id).update({
        models.User.nickname: update_data["nickname"],
        models.User.profile_image: update_data["profile_image"]
    }, synchronize_session=False)
    db.commit()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user_points(db: Session, user_id: int, new_points: int):
    # 사용자 포인트 업데이트
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise ValueError("User not found")

    user.user_point = new_points
    db.commit()
    db.refresh(user)

    # 랭킹 업데이트
    ranking = db.query(models.Ranking).filter(models.Ranking.user_id == user_id).first()
    if ranking is None:
        # 랭킹이 없으면 새로 생성
        ranking = models.Ranking(user_id=user_id, user_point=new_points)
        db.add(ranking)
    else:
        # 랭킹이 있으면 업데이트
        ranking.user_point = new_points
    db.commit()
    db.refresh(ranking)

    # 랭킹 재정렬
    update_rankings(db)


def update_rankings(db: Session):
    # 모든 랭킹 데이터를 가져와서 포인트로 정렬
    rankings = db.query(models.Ranking).order_by(models.Ranking.user_point.desc()).all()

    # 랭킹 업데이트
    for rank, ranking in enumerate(rankings, start=1):
        ranking.ranking_position = rank
    db.commit()


###################################################################


# Scripts 모델을 위한 CRUD 함수들
def get_script(db: Session, scripts_id: int):
    return db.query(Scripts).filter(Scripts.scripts_id == scripts_id).first()


def create_script(db: Session, script_data):
    new_script = Scripts(
        level=script_data['level'],
        category_id=script_data['category_id'],
        content_1=script_data['content_1'],
        content_2=script_data['content_2'],
        content_3=script_data['content_3']
    )
    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    return new_script.scripts_id


def update_script(db: Session, script_id: int, update_data):
    script = db.query(Scripts).filter(Scripts.scripts_id == script_id).first()
    if script:
        for key, value in update_data.items():
            setattr(script, key, value)
        db.commit()
        db.refresh(script)
        return script
    return None


def delete_script(db: Session, script_id: int):
    script = db.query(Scripts).filter(Scripts.scripts_id == script_id).first()
    if script:
        db.delete(script)
        db.commit()
        return True
    return False


def get_scripts_by_category(db: Session, category_name: int):
    return db.query(Scripts).filter(Scripts.category_name == category_name).all()


###################################################################
# Question
def create_question(db: Session, question_data):
    question = Question(
        scripts_id=question_data['scripts_id'],
        answer_option=question_data['answer_option'],
        question=question_data['question'],
        option_1=question_data['option_1'],
        option_2=question_data['option_2'],
        option_3=question_data['option_3'],
        option_4=question_data['option_4'],
        plus_point=question_data['plus_point'],
        minus_point=question_data['minus_point']
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_question_by_script_id(db: Session, scripts_id: int):
    return db.query(Question).filter(Question.scripts_id == scripts_id).first()


def update_question(db: Session, q_id: int, update_data):
    question = db.query(Question).filter(Question.q_id == q_id).first()
    if question:
        if 'answer_option' in update_data:
            question.answer_option = update_data['answer_option']
        if 'question' in update_data:
            question.question = update_data['question']
        if 'option_1' in update_data:
            question.option_1 = update_data['option_1']
        if 'option_2' in update_data:
            question.option_2 = update_data['option_2']
        if 'option_3' in update_data:
            question.option_3 = update_data['option_3']
        if 'option_4' in update_data:
            question.option_3 = update_data['option_4']
        db.commit()
        return question
    return None


def get_category_by_content(db: Session, content: str):
    return db.query(Category).filter(Category.content == content).first()


def get_categories(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Category).offset(skip).limit(limit).all()


def get_cotegory_name_by_category_id(db: Session, category_id: int):
    all_db = db.query(Category).filter(Category.category_id == category_id).first()

    return all_db.content


def create_category(db: Session, category_in: CategoryCreate):
    db_obj = Category(
        content=category_in.content,
        label=category_in.label,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_category(db: Session, category_id: int, category_in: CategoryUpdate):
    db_obj = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_obj:
        return None
    for field, value in category_in.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_category(db: Session, category_id: int):
    db_obj = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_obj:
        return None
    db.delete(db_obj)
    db.commit()
    return db_obj


###################################################################
def create_case_script(db: Session, case_script_data):
    new_case_script = CaseScripts(
        scripts_id=case_script_data['scripts_id'],
        content_1=case_script_data['content_1'],
        content_2=case_script_data['content_2'],
        content_3=case_script_data['content_3'],
        content_4=case_script_data['content_4'],
        content_5=case_script_data['content_5'],
        content_6=case_script_data['content_6']
    )
    db.add(new_case_script)
    db.commit()
    db.refresh(new_case_script)
    return new_case_script


def get_case_script(db: Session, case_scripts_id: int):
    return db.query(CaseScripts).filter(CaseScripts.case_scripts_id == case_scripts_id).first()


def get_case_scripts_by_script_id(db: Session, scripts_id: int):
    return db.query(CaseScripts).filter(CaseScripts.scripts_id == scripts_id).first()


def update_case_script(db: Session, scripts_id: int, update_case_data: dict):
    case_script = db.query(CaseScripts).filter(CaseScripts.scripts_id == scripts_id).first()

    if not case_script:
        return None

    for key, value in update_case_data.items():
        if value is not None:
            print(f"Updating {key} to {value}")  # 디버깅을 위해 추가
            setattr(case_script, key, value)

    db.commit()
    db.refresh(case_script)
    return case_script


def delete_case_script(db: Session, case_scripts_id: int):
    case_script = db.query(CaseScripts).filter(CaseScripts.case_scripts_id == case_scripts_id).first()
    if not case_script:
        return None
    db.delete(case_script)
    db.commit()
    return case_script


# comment
def create_comment(db: Session, comment_data):
    comment = Comment(
        q_id=comment_data['q_id'],
        comment_1=comment_data['comment_1'],
        comment_2=comment_data['comment_2'],
        comment_3=comment_data['comment_3'],
        comment_4=comment_data['comment_4']
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


# 업데이트 함수 정의
def update_comment(db: Session, q_id: int, update_data):
    db_comment = db.query(Comment).filter(Comment.q_id == q_id).first()
    if not db_comment:
        return None

    if 'comment_1' in update_data:
        db_comment.comment_1 = update_data['comment_1']
    if 'comment_2' in update_data:
        db_comment.comment_2 = update_data['comment_2']
    if 'comment_3' in update_data:
        db_comment.comment_3 = update_data['comment_3']
    if 'comment_4' in update_data:
        db_comment.comment_4 = update_data['comment_4']

    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment_by_script_id(db: Session, scripts_id: int):
    # 스크립트 ID를 사용하여 질문을 찾습니다.
    question = db.query(Question).filter(Question.scripts_id == scripts_id).first()
    if not question:
        return None
    comment = db.query(Comment).filter(Comment.q_id == question.q_id).first()
    return comment


# Shortform
def create_shortform(db: Session, shortform_data):
    new_shortform = Shortform(
        form_url=shortform_data['form_url'],
        scripts_id=shortform_data['scripts_id']
    )
    db.add(new_shortform)
    db.commit()
    db.refresh(new_shortform)
    return new_shortform


def get_shortform_by_id(db: Session, form_id: int):
    return db.query(Shortform).filter(Shortform.form_id == form_id).first()


def get_shortform_by_scripts_id(db: Session, scripts_id: int):
    return db.query(Shortform).filter(Shortform.scripts_id == scripts_id).first()


# 가장 최근에 추가된 shortform 데이터를 읽어오는 함수
def get_latest_shortform(db):
    return db.query(Shortform).order_by(desc(Shortform.form_id)).first()


# admin
def get_admin_by_admin_name(db: Session, admin_name: str):
    return db.query(Admin).filter(Admin.admin_name == admin_name).first()




def create_admin(db: Session, admin_data: dict, admin_id: int, pwd_context):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin and admin.qualification_level == 3:
        hashed_password = pwd_context.hash(admin_data['password'])
        new_admin = Admin(
            admin_name=admin_data['admin_name'],
            password=hashed_password,
            qualification_level=admin_data['qualification_level']
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        return new_admin
    return False


def delete_admin_if_level_3(db: Session, admin_id: int):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin and admin.qualification_level == 3:
        db.delete(admin)
        db.commit()
        return True
    return False


def get_admin_level(db: Session, admin_id: int):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin:
        return admin.qualification_level
    return None


def update_admin(db: Session, admin_data: dict):
    admin_id = admin_data.get("admin_id")
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin:
        if "qualification_level" in admin_data:
            admin.qualification_level = admin_data["qualification_level"]

            db.commit()
            db.refresh(admin)
            return admin
    return None


# history

def create_user_history(db: Session, user_id: int, script_id: int, T_F: bool):
    user_history = History(user_id=user_id, script_id=script_id, T_F=T_F)
    db.add(user_history)
    db.commit()
    db.refresh(user_history)
    return user_history


def update_user_history(db: Session, user_id: int, script_id: int):
    user_history = db.query(History).filter(History.user_id == user_id, History.script_id == script_id).first()
    if user_history:
        user_history.time += 1
        if user_history.time == 3:
            user_history.T_F = True
        db.commit()
        db.refresh(user_history)
    return user_history


def get_user_history(db: Session, user_id: int, T_F: bool = None):
    query = db.query(History).filter(History.user_id == user_id)
    if T_F is not None:
        query = query.filter(History.T_F == T_F)
    return query.all()


# ranking

def create_ranking(db: Session, ranking_data):
    ranking = Ranking(
        user_id=ranking_data['user_id'],
        user_point=ranking_data['user_point']
    )
    db.add(ranking)
    db.commit()
    db.refresh(ranking)
    return ranking


def update_ranking_points(db: Session, user_id: int, new_points):
    ranking = db.query(Ranking).filter(Ranking.user_id == user_id).first()
    if ranking:
        ranking.user_point = new_points
        db.commit()
        return ranking
    return None
