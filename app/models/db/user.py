from datetime import date

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    username: str
    password: str
    email: EmailStr
    role: int | None
    name: str
    birthday: date | None
    info: str | None
    interests: str | None
    rank: int | None
    rating: int
