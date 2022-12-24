from pydantic import BaseModel


class SubscribtionResponse(BaseModel):
    user: int
    event: int
    message: str
