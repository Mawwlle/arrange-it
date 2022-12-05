from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.exceptions import EntityDuplicateException
from app.models import representation
from app.services.user import create_user
from app.services.user.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    user = await authenticate_user(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


class RegistrationResponse(BaseModel):
    message: str
    status_code: int


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def register_a_new_user(
    user: representation.UserRegistration,
) -> RegistrationResponse:
    await create_user(user)

    return RegistrationResponse(
        message="User created successfully", status_code=status.HTTP_201_CREATED
    )
