from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
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



