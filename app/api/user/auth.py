from datetime import timedelta

from asyncpg import Record
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import representation, db
from app.services.user import add_user
from app.services.user.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.nickname}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/sign_in", status_code=status.HTTP_201_CREATED)
async def register_a_new_user(user: db.User) -> Record:
    return await add_user(user)
