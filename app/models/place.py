from pydantic import BaseModel


class Point(BaseModel):
    x: float
    y: float


class Place(BaseModel):
    id: int
    name: str
    point: Point


class PlaceResponse(BaseModel):
    id: int
    name: str
    point: Point
    message: str
