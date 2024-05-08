from sqlalchemy.orm import Session

from app.core.db import models, schemas
from app.core.db.models import Scripts, Question, Shortform, Comment, Admin, History, Ranking


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Scripts 스크립트
def create_script(db: Session, script_data):
    new_script = Scripts(
        level=script_data['level'],
        category_name=script_data['category_name'],
        content_1=script_data['content_1'],
        content_2=script_data['content_2'],
        content_3=script_data['content_3']
    )
    db.add(new_script)
    db.commit()
    db.refresh(new_script)
    return new_script


def get_script_by_id(db: Session, script_id: int):
    return db.query(Scripts).filter(Scripts.scripts_id == script_id).first()


def update_script(db: Session, script_id: int, update_data):
    script = db.query(Scripts).filter(Scripts.scripts_id == script_id).first()
    if script:
        for key, value in update_data.items():
            setattr(script, key, value)
        db.commit()
        return script
    return None


def delete_script(db: Session, script_id: int):
    script = db.query(Scripts).filter(Scripts.scripts_id == script_id).first()
    if script:
        db.delete(script)
        db.commit()
        return True
    return False


def get_scripts_by_category(db: Session, category_name: str):
    return db.query(Scripts).filter(Scripts.category_name == category_name).all()


# Question
def create_question(db: Session, question_data):
    question = Question(
        scripts_id=question_data['scripts_id'],
        answer_option=question_data['answer_option'],
        question=question_data['question'],
        option_1=question_data['option_1'],
        option_2=question_data['option_2'],
        option_3=question_data['option_3'],
        plus_point=question_data['plus_point'],
        minus_point=question_data['minus_point']
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


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
        if 'plus_point' in update_data:
            question.plus_point = update_data['plus_point']
        if 'minus_point' in update_data:
            question.minus_point = update_data['minus_point']

        db.commit()
        return question
    return None


# comment
def create_comment(db: Session, comment_data):
    comment = Comment(
        q_id=comment_data['q_id'],
        comment_1=comment_data['comment_1'],
        comment_2=comment_data['comment_2'],
        comment_3=comment_data['comment_3']
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_by_question_id(db: Session, q_id: int):
    return db.query(Comment).filter(Comment.q_id == q_id).all()


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


# admin

def create_admin(db: Session, admin_data):
    admin = Admin(
        password=admin_data['password']
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def delete_admin(db: Session, admin_id: int):
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
    if admin:
        db.delete(admin)
        db.commit()
        return True
    return False


# history

def log_history(db: Session, history_data):
    history = History(
        user_id=history_data['user_id'],
        scripts_id=history_data['scripts_id'],
        T_F=history_data['T_F']
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


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
