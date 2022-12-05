from datetime import date

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr
    role: int
    name: str
    birthday: date
    info: str
    interests: str
    rank: int
    rating: int
