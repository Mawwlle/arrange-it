from datetime import date

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Базовое отображение пользователя
    Вся информация кроме пароля
    """

    id: int
    name: str
    username: str
    email: EmailStr
    role: int | None
    birthday: date | None
    info: str | None
    interests: str | None
    rank: int | None
    rating: int | None
    verified: bool


class UserDB(BaseModel):
    """Базовое отображение пользователя
    Вся информация кроме пароля
    """

    id: int
    name: str
    username: str
    email: EmailStr
    password: str
    role: int | None
    birthday: date | None
    info: str | None
    interests: str | None
    rank: int | None
    rating: int | None
    verified: bool

    def to_representation(self) -> User:
        """Перевод модели в репрезентативную форму"""
        return User(
            id=self.id,
            name=self.name,
            username=self.username,
            email=self.email,
            birthday=self.birthday,
            info=self.info,
            interests=self.interests,
            rank=self.rank,
            rating=self.rating,
            role=self.role,
            verified=self.verified,
        )


class Admin(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr


class AdminDB(BaseModel):

    id: int
    name: str
    username: str
    email: EmailStr
    password: str

    def to_representation(self) -> Admin:
        """Перевод модели в репрезентативную форму"""

        return Admin(
            id=self.id,
            name=self.name,
            username=self.username,
            email=self.email,
        )


class UserRegistration(BaseModel):
    """Модель используемая для регистрации пользователей"""

    name: str
    username: str
    email: EmailStr
    password: str
