import random
from typing import Any, List

from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from app.core.db import models, schemas
from app.core.db.models import Scripts, Question, Shortform, Admin, History, Ranking, CaseScripts, Comment, Category, \
    User, Profile_images
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


def get_user_for_password(db: Session, e_mail: str, name: str):
    return db.query(User).filter(User.e_mail == e_mail, User.name == name).first()


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


def get_random_category_content_by_label(db: Session, label: int):
    print("a")
    categories = db.query(models.Category).filter(models.Category.label == label).all()
    if not categories:
        return None
    random_category = random.choice(categories)
    print(random_category.content)
    return random_category.content


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    new_category = models.Category(content=category.content, label=category.label)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


###################################################################


# Scripts 모델을 위한 CRUD 함수들
def get_script(db: Session, scripts_id: int):
    return db.query(Scripts).filter(Scripts.scripts_id == scripts_id).first()


def get_scripts_by_inspection_status(db: Session, inspection_status: bool):
    try:
        return db.query(Scripts).join(Category, Scripts.category_id == Category.category_id).filter(
            Scripts.inspection_status == inspection_status).all()
    except Exception as e:
        print(f"Error fetching scripts: {e}")
        return None


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


def create_categories(db: Session, category_in: CategoryCreate):
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


def get_admins(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Admin).filter(models.Admin.qualification_level != 3).offset(skip).limit(limit).all()


def get_admin_count(db: Session):
    return db.query(models.Admin).count()


def get_admins_mobile(db: Session):
    return db.query(models.Admin).filter(models.Admin.qualification_level != 3).all()


# 가장 최근에 추가된 shortform 데이터를 읽어오는 함수
def get_latest_shortform(db):
    return db.query(Shortform).order_by(desc(Shortform.form_id)).first()


# admin
def get_admin_by_admin_name(db: Session, admin_name: str) -> object:
    db_admin = db.query(Admin).filter(Admin.admin_name == admin_name).first()
    return db_admin.qualification_level


def get_active_admin_by_admin_name(db: Session, admin_name: str):
    return db.query(Admin).filter(Admin.admin_name == admin_name, Admin.account_status == True).first()


def create_admin(db: Session, admin: schemas.AdminCreate):
    db_admin = Admin(
        admin_name=admin.admin_name,
        qualification_level=admin.qualification_level,
        password=admin.password,
        account_status=True
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin


def update_admin(db: Session, admin_id: int, admin_update: schemas.AdminUpdate):
    db_admin = db.query(models.Admin).filter(models.Admin.admin_id == admin_id).first()
    if not db_admin:
        return None
    db_admin.qualification_level = admin_update.qualification_level
    db_admin.account_status = admin_update.account_status
    db.commit()
    db.refresh(db_admin)
    return db_admin


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


def check_admin_password(db: Session, password: str):
    admin = db.query(Admin).filter(Admin.qualification_level == 3).first()  # level 3 관리자 계정 확인
    if not admin:
        return "fail"
    if admin.password == password:  # 평문 비밀번호 비교
        return "success"
    else:
        return "fail"


def get_user_password(db: Session, admin_id: int):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin:
        return admin.password  # 실제 서비스에서는 비밀번호를 반환하는 대신 다른 보안 조치를 고려해야 함
    return None


def create_user_history(db: Session, user_id: int, script_id: int, T_F: bool):
    user_history = History(user_id=user_id, scripts_id=script_id, T_F=T_F)
    db.add(user_history)
    db.commit()
    db.refresh(user_history)
    return user_history


async def update_user_history(db: Session, user_id: int, script_id: int):
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


def get_user_by_email_and_name(db: Session, email: str, name: str):
    return db.query(User).filter(User.e_mail == email, User.name == name).first()


def get_user_by_nickname_and_name(db: Session, nickname: str, name: str):
    return db.query(User).filter(User.nickname == nickname, User.name == name).first()


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


def get_ranking(db: Session):
    ranking = (
        db.query(Ranking.ranking_position, Ranking.user_id, User.nickname, Ranking.user_point)
        .join(User, Ranking.user_id == User.user_id)
        .filter(Ranking.ranking_position <= 3)
        .order_by(Ranking.ranking_position)
        .all()
    )

    # ranking은 이제 (ranking_position, user_id, nickname, points) 형태의 튜플 리스트입니다.
    result = []
    for ranking_position, user_id, nickname, user_point in ranking:
        result.append({
            'ranking_position': ranking_position,
            'user_id': user_id,
            'nickname': nickname,
            'points': user_point
        })
    return result


# 생성된 문제 개수
def get_created_problem_count(db: Session):
    count = db.query(func.count(Scripts.scripts_id)).scalar()
    return count


# 검토 완료된 문제 개수4
def get_true_questions_count(db: Session):
    count = db.query(func.count(Scripts.scripts_id)).filter(Scripts.inspection_status == True).scalar()
    return count


# 사용자 수
def get_user_count(db: Session):
    count = db.query(func.count(User.user_id)).scalar()
    return count


def update_inspection_status(db: Session, scripts_id: int):
    script = db.query(Scripts).filter(Scripts.scripts_id == scripts_id).first()
    if script:
        script.inspection_status = True
        db.commit()

    return script.inspection_status


def get_scripts(db: Session):
    return db.query(Scripts).all()


def get_random_script_by_category_label_and_level(db: Session, category_label: int, level: int):
    # 1. Find all categories with the given label
    categories = db.query(Category).filter(Category.label == category_label).all()

    if not categories:
        return None  # No categories found with the given label

    # 2. Randomly select one of these categories
    selected_category = random.choice(categories)

    # 3. Find all scripts with the selected category_id, level, and inspection_status True
    scripts = db.query(Scripts).filter(
        Scripts.category_id == selected_category.category_id,
        Scripts.level == level,
        Scripts.inspection_status == True
    ).all()

    if not scripts:
        return None  # No scripts found with the given category_id, level, and inspection_status True

    # 4. Randomly select and return one of these scripts
    return random.choice(scripts)


def get_shortforms_by_scripts_id(db: Session, scripts_id: int):
    return db.query(Shortform).filter(Shortform.scripts_id == scripts_id).all()


def get_questions_by_scripts_id(db: Session, scripts_id: int):
    return db.query(Question).filter(Question.scripts_id == scripts_id).all()


def get_comments_by_q_id(db: Session, q_id: int):
    return db.query(Comment).filter(Comment.q_id == q_id).all()


def get_questions(db: Session):
    return db.query(Question).all()


def get_comments(db: Session):
    return db.query(Comment).all()


def get_case_scripts(db: Session):
    return db.query(CaseScripts).all()


def get_shortform(db: Session):
    return db.query(Shortform).all()


def get_profile_image_url(user_id: int, db: Session) -> str:
    result = db.query(Profile_images.image_url). \
        join(User, User.profile_image == Profile_images.image_id). \
        filter(User.user_id == user_id).first()
    return result.image_url if result else None


def get_random_quizzes(db: Session, limit: int = 10):
    quizzes = db.query(models.Enrollment_quiz).all()
    return random.sample(quizzes, limit)


def get_correct_answers(db: Session, quiz_ids: List[int]):
    quizzes = db.query(models.Enrollment_quiz).filter(models.Enrollment_quiz.enrollment_quiz_id.in_(quiz_ids)).all()
    return {quiz.enrollment_quiz_id: quiz.correct for quiz in quizzes}
