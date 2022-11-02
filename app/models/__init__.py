from pydantic import EmailStr
from pydantic.main import BaseModel


class PostSchema(BaseModel):
    id: int | None = None
    title: str | None = None
    content: str | None = None

    class Config:
        schema_extra = {
            "port_demo": {
                "title": "some title about animals",
                "content": "some content about animals",
            }
        }


class UserSchema(BaseModel):
    fullname: str | None = None
    email: EmailStr | None = None
    password: str | None = None

    class Config:
        the_schema = {
            "user_demo": {
                "name": "Bek",
                "email": "help@bekbrace.com",
                "password": "123",
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

    class Config:
        the_schema = {"user_demo": {"email": "help@bekbrace.com", "password": "123"}}
