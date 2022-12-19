# верификация пользователей
# верификация мероприятий
# удаление пользователей


from fastapi import APIRouter, HTTPException, Security, status

from app.dependencies import anauthorized_exception, get_current_user
from app.models.responses import UserResponse
from app.models.user import User
from app.services import user

router = APIRouter(tags=["administration"])


async def check(current_user: User, username: str, err_msg: str) -> None:
    if not current_user:
        raise anauthorized_exception

    if current_user.info.username == username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are cannot change your account!",
        )


@router.delete("/user")
async def deleting_user(
    username: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> UserResponse:
    """Удаление конкретного пользователя"""

    await check(current_user, username, err_msg="You are cannot delete your account!")

    return await user.delete(username)


@router.patch("/verify")
async def verify_user(
    username: str, current_user: User = Security(get_current_user, scopes=["administrator"])
) -> UserResponse:
    """Верификация пользователя"""

    await check(current_user, username, err_msg="Could not verify yourself!")

    return await user.verify(username)


# @router.post("/verify/event")
# async def verify_event(
#     event: int, current_user: User | None = Depends(get_current_user)
# ) -> VerificationResponse:
#     """Верификация мероприятий"""
#     pass
