from fastapi import HTTPException, status

from app.dependencies import anauthorized_exception
from app.models.user import User
from app.services import event, user


async def check(current_user: User, err_msg: str) -> None:
    if not current_user:
        raise anauthorized_exception

    if not current_user.meta.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err_msg,
        )


async def is_user_owner(current_user: User, event_id: int) -> None:
    user_id = await user.misc.get_id_by(current_user.info.username)
    organizer_id = await event.get_organizer_id_by(event_id)

    if user_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't change someone else's event! The user can only chage their own events",
        )
