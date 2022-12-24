"""API для идентификации пользователей"""
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token", status_code=status.HTTP_200_OK)
async def jwt_auth(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    """Получение токена"""

    user = await authenticate_user(form_data.username, form_data.password, form_data.scopes)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
