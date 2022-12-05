from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    nickname: str
    password: str
    email: EmailStr
    role: int
    name: str
    age: int
    info: str
    interests: str
    rank: int
    rating: int
