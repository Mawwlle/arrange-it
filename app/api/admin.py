from turtle import hideturtle

from fastapi import APIRouter, HTTPException, Security, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models.responses import BaseResponse, UserResponse
from app.models.user import User
from app.services import admin, user

router = APIRouter(tags=["administration"])


async def check(current_user: User, username: str, err_msg: str) -> None:
    if not current_user:
        raise anauthorized_exception

    if current_user.username == username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are cannot change your account!",
        )


@router.delete("/{username}", status_code=status.HTTP_200_OK)
async def deleting_user(
    username: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> UserResponse:
    """Удаление конкретного пользователя"""

    await check(current_user, username, err_msg="You are cannot delete your account!")

    return await user.delete(username)


@router.post("/admin/{username}", status_code=status.HTTP_201_CREATED)
async def create_admin_normal(
    username: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> UserResponse:
    """Создание пользователя конкретного пользователя"""

    return await admin.create(username)


@router.post("/bla_bla/just/hook/for/admin/creation", status_code=status.HTTP_201_CREATED)
async def create_admin_faster(username: str) -> UserResponse:
    """Просто для разработки чтобы быстрее было создавать админов"""

    return await admin.create(username)


@router.delete("/admin/{username}", status_code=status.HTTP_201_CREATED)
async def create_admin(
    username: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> UserResponse:
    """Создание пользователя конкретного пользователя"""

    return await admin.delete(username)


@router.patch("/verify/{username}", status_code=status.HTTP_200_OK)
async def verify_user(
    username: str, current_user: User = Security(get_current_user, scopes=["administrator"])
) -> UserResponse:
    """Верификация пользователя"""

    await check(current_user, username, err_msg="Could not verify yourself!")

    return await user.verify(username)


@router.patch("/verify/{event_id}", status_code=status.HTTP_200_OK)
async def verify_event(
    event_id: int, current_user: User = Security(get_current_user, scopes=["administrator"])
) -> BaseResponse:
    """Верификация мероприятий"""

    return await services.event.verify(event_id)
