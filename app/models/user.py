from datetime import date

from pydantic import BaseModel, EmailStr


class UserBaseInfo(BaseModel):
    """Базовая информация о пользователе"""

    full_name: str
    username: str
    email: EmailStr


class UserMetaInfo(BaseModel):
    """Дополнительная информация о пользователе"""

    role: int | None
    birthday: date | None
    info: str | None
    interests: str | None
    rank: int | None
    rating: int | None


class UserDBMapping(BaseModel):
    """Отображение информации о пользователе из базы данных"""

    info: UserBaseInfo
    meta: UserMetaInfo
    password: str


class User(BaseModel):
    """Базовое отображение пользователя
    Вся информация кроме пароля
    """

    info: UserBaseInfo
    meta: UserMetaInfo


class UserRegistration(BaseModel):
    """Модель используемая для регистрации пользователей"""

    info: UserBaseInfo
    password: str
