from datetime import datetime

from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Ответ на регистрацию"""

    message: str
    id: int


class UserResponse(BaseModel):
    """Ответ на удаление пользователей"""

    message: str
    username: str
    id: int


class CommentResponse(BaseModel):
    text: str
    time: datetime
    user: int
    event: int
