"""API для идентификации пользователей"""
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app import services
from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.responses import BaseResponse
from app.models.user import UserRegistration
from app.services.user.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token")
async def jwt_auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    """Получение токена"""

    user = await authenticate_user(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.info.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def register_a_new_user(
    user: UserRegistration,
) -> BaseResponse:
    """Регистрация нового пользователя"""

    user_id = await services.user.create(user)

    return BaseResponse(message="User created successfully", id=user_id)
