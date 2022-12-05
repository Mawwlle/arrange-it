from datetime import date

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    role: int | None
    name: str
    birthday: date | None
    info: str | None
    interests: str | None
    rank: int | None
    rating: int | None


class UserRegistration(BaseModel):
    full_name: str
    username: str
    password: str
    email: EmailStr
