from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    e_mail = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String, index=True)
    nickname = Column(String, unique=True, index=True)
    level = Column(String, default="0")
    user_point = Column(Integer, index=True, default="0")
    profile_image = Column(Integer, ForeignKey("profile_images.image_id"))
    is_active = Column(Boolean, default=True)

    histories = relationship("History", back_populates="users")
    rankings = relationship("Ranking", back_populates="users")
    profile_images = relationship("Profile_images")


class Profile_images(Base):
    __tablename__ = "profile_images"
    image_id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)


# users의 point를 내림차순으로 만들고 ranking을 매김
class Ranking(Base):
    __tablename__ = "ranking"
    r_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    user_point = Column(Integer, index=True)
    ranking_position = Column(Integer, index=True)  # 랭킹 순위 필드 추가

    users = relationship("User", back_populates="rankings")


class Scripts(Base):
    __tablename__ = "scripts"
    scripts_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(Integer, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    inspection_status = Column(Boolean, default=False)
    content_1 = Column(String)
    content_2 = Column(String)
    content_3 = Column(String)

    histories = relationship("History", back_populates="scripts")
    questions = relationship("Question", back_populates="scripts")
    shortform = relationship("Shortform", back_populates="scripts")
    categories = relationship("Category", back_populates="scripts")


class CaseScripts(Base):
    __tablename__ = "caseScripts"
    case_scripts_id = Column(Integer, primary_key=True, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    content_1 = Column(String)
    content_2 = Column(String)
    content_3 = Column(String)
    content_4 = Column(String)
    content_5 = Column(String)
    content_6 = Column(String)

    shortform = relationship("Shortform", back_populates="caseScripts")


class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    label = Column(Integer)  # label is not unique

    scripts = relationship("Scripts", back_populates="categories")


class Shortform(Base):
    __tablename__ = "shortform"
    form_id = Column(Integer, primary_key=True, index=True)
    form_url = Column(String, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    case_scripts_id = Column(Integer, ForeignKey("caseScripts.case_scripts_id"))

    scripts = relationship("Scripts", back_populates="shortform")
    caseScripts = relationship("CaseScripts", back_populates="shortform")


class Question(Base):
    __tablename__ = "question"
    q_id = Column(Integer, primary_key=True, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    answer_option = Column(Integer)
    question = Column(String)
    option_1 = Column(String)
    option_2 = Column(String)
    option_3 = Column(String)
    option_4 = Column(String)
    plus_point = Column(Integer)
    minus_point = Column(Integer)

    scripts = relationship("Scripts", back_populates="questions")
    comments = relationship("Comment", back_populates="questions")


class Comment(Base):
    __tablename__ = "comment"
    c_id = Column(Integer, primary_key=True, index=True)
    q_id = Column(Integer, ForeignKey("question.q_id"))
    comment_1 = Column(String)
    comment_2 = Column(String)
    comment_3 = Column(String)
    comment_4 = Column(String)
    questions = relationship("Question", back_populates="comments")


class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True, index=True)
    admin_name = Column(String)
    password = Column(String)
    qualification_level = Column(Integer)


class History(Base):
    __tablename__ = "history"
    h_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    T_F = Column(Boolean)
    time = Column(Integer, default=0)

    users = relationship("User", back_populates="histories")
    scripts = relationship("Scripts", back_populates="histories")
