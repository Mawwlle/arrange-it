from pydantic import BaseModel


class Tag(BaseModel):
    id: int
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
    message: str
