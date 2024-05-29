from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str
    nickname: str
    e_mail: str
    level: str = "1"
    user_point: int = 0
    profile_image: int


class UserCreate(UserBase):
    hashed_password: str


class UserRead(UserBase):
    is_active: bool
    user_id: int


class PointsUpdate(BaseModel):
    user_point: int


# class RankingBase(BaseModel):
#     user_id: int
#     user_point: int
#
#
# class RankingCreate(RankingBase):
#     pass
#
#
# class RankingRead(RankingBase):
#     r_id: int
#
#
# class RankingUpdate(BaseModel):
#     user_point: Optional[int] = None


class Login(BaseModel):
    e_mail: str
    password: str


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    profile_image: Optional[int] = None


class ScriptsBase(BaseModel):
    level: int
    category_name: int
    content_1: str
    content_2: str
    content_3: str


class ScriptsCreate(ScriptsBase):
    pass


class ScriptsRead(ScriptsBase):
    scripts_id: int


class ScriptsUpdate(ScriptsBase):
    pass


class ShortformBase(BaseModel):
    form_url: str
    scripts_id: int


class ShortformCreate(ShortformBase):
    pass


class ShortformRead(ShortformBase):
    form_id: int


class ShortformUpdate(BaseModel):
    form_url: Optional[str] = None


class QuestionBase(BaseModel):
    scripts_id: int
    answer_option: int
    question: int
    option_1: str
    option_2: str
    option_3: str
    plus_point: str
    minus_point: str


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    q_id: int


class QuestionUpdate(BaseModel):
    answer_option: Optional[int] = None
    question: Optional[int] = None
    option_1: Optional[str] = None
    option_2: Optional[str] = None
    option_3: Optional[str] = None
    plus_point: Optional[str] = None
    minus_point: Optional[str] = None


class CommentBase(BaseModel):
    q_id: int
    comment_1: str
    comment_2: str
    comment_3: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    c_id: int


class CommentUpdate(BaseModel):
    comment_1: Optional[str] = None
    comment_2: Optional[str] = None
    comment_3: Optional[str] = None


class AdminBase(BaseModel):
    password: str


class AdminCreate(AdminBase):
    pass


class AdminRead(AdminBase):
    admin_id: int


class AdminUpdate(BaseModel):
    password: Optional[str] = None


class HistoryBase(BaseModel):
    user_id: int
    scripts_id: int
    T_F: bool


class HistoryCreate(HistoryBase):
    pass


class HistoryRead(HistoryBase):
    h_id: int


class HistoryUpdate(BaseModel):
    T_F: Optional[bool] = None
