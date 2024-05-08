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
    level = Column(String)
    user_point = Column(String, index=True)

    is_active = Column(Boolean, default=True)

    histories = relationship("History", back_populates="users")
    rankings = relationship("Ranking", back_populates="users")
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
    category_name = Column(String)
    content_1 = Column(String)
    content_2 = Column(String)
    content_3 = Column(String)

    histories = relationship("History", back_populates="scripts")
    questions = relationship("Question", back_populates="scripts")
    shortform = relationship("Shortform", back_populates="scripts")
    admins = relationship("Admin", back_populates="scripts")

class Shortform(Base):
    __tablename__ = "shortform"
    form_id = Column(Integer, primary_key=True, index=True)
    form_url = Column(String, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    scripts = relationship("Scripts", back_populates="shortform")


class Question(Base):
    __tablename__ = "question"
    q_id = Column(Integer, primary_key=True, index=True)
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    answer_option = Column(Integer)
    question = Column(Integer)
    option_1 = Column(String)
    option_2 = Column(String)
    option_3 = Column(String)
    plus_point = Column(String)
    minus_point = Column(String)

    scripts = relationship("Scripts", back_populates="questions")
    # comments = relationship("Comment", back_populates="questions")



# class Comment(Base):
#     __tablename__ = "comment"
#     q_id = Column(Integer, ForeignKey("question.q_id"))
#     comment_1 = Column(String)
#     comment_2 = Column(String)
#     comment_3 = Column(String)
#     questions = relationship("Question", back_populates="comments")



class Admin(Base):
    __tablename__ = "admin"
    admin_id = Column(Integer, primary_key=True, index=True)
    password = Column(String)
    scripts = relationship("Scripts", back_populates="admins")



class History(Base):
    __tablename__ = "history"
    h_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    scripts_id = Column(Integer, ForeignKey("scripts.scripts_id"))
    T_F = Column(Boolean)
    users = relationship("User", back_populates="histories")

    scripts = relationship("Scripts", back_populates="histories")



# users의 point를 내림차순으로 만들고 ranking을 매김
class Ranking(Base):
    __tablename__ = "ranking"
    r_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    user_point = Column(String, ForeignKey("users.user_point"))

    users = relationship("User", back_populates="rankings")

