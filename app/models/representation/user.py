from datetime import date

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr
    role: int
    name: str
    birthday: date
    info: str
    interests: str
    rank: int
    rating: int


class UserRegistration(BaseModel):
    full_name: str
    username: str
    password: str
    email: str
    birthday: date
