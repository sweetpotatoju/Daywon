from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    nickname = Column(String, index=True)
    hashed_password = Column(String)
    e_mail = Column(String, unique=True, index=True)
    level = Column(String, index=True)
    user_point = Column(String, index=True)

    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")


class Scripts(Base):
    __tablename__ = "scripts"
    scripts_id = Column(Integer, primary_key=True, index=True)
    level = Column(Integer, index=True)
    category_name = Column(String, index=True)
    content_1 = Column(String, index=True)
    content_2 = Column(String, index=True)
    content_3 = Column(String, index=True)


class Shortform(Base):
    __tablename__ = "shortform"
    form_id = Column(Integer, primary_key=True, index=True)
    form_url = Column(String, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))


class Question(Base):
    __tablename__ = "question"
    q_id = Column(Integer, primary_key=True, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    answer_option = Column(Integer, index=True)
    question = Column(Integer, index=True)
    option_1 = Column(String, index=True)
    option_2 = Column(String, index=True)
    option_3 = Column(String, index=True)
    plus_point = Column(String, index=True)
    minus_point = Column(String, index=True)


class Comment(Base):
    __tablename__ = "comment"
    q_id = Column(Integer, ForeignKey("question.q_id"))
    comment_1 = Column(String, index=True)
    comment_2 = Column(String, index=True)
    comment_3 = Column(String, index=True)


class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True, index=True)
    password = Column(String)


class History(Base):
    __tablename__ = "history"
    h_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    T_F = Column(Boolean, index=True)


# users의 point를 내림차순으로 만들고 ranking을 매김
class Ranking(Base):
    __tablename__ = "ranking"
    r_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    user_point = Column(String, ForeignKey("users.user_point"))
