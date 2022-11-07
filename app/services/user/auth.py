from datetime import datetime, timedelta

import jwt

from app.dependencies import ALGORITHM, SECRET_KEY, get_user_db
from app.misc import verify_password
from app.models import representation


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def authenticate_user(username: str, password: str) -> bool | representation.User:
    user = await get_user_db(username)

    if not user:
        return False

    if not await verify_password(password, user.password):
        return False

    return representation.User(
        nickname=user.nickname,
        email=user.email,
        name=user.name,
        age=user.age,
        info=user.info,
        interests=user.interests,
        rating=user.rating,
    )
