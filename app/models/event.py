from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

from app.models.user import User


class State(str, Enum):
    PENDING_APPROVAL = "pending approval"
    ACTIVE = "active"
    ENDED = "ended"
    REJECTED = "rejected"


class Point(BaseModel):
    x: float
    y: float


class Place(BaseModel):
    name: str
    point: Point


class Event(BaseModel):
    """Дополнительная информация о пользователе"""

    place: str
    time: datetime
    description: str


class EventDBMapping(BaseModel):
    organizer: User
    place: Place
    state: State
    date: date
