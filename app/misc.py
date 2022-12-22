from fastapi import HTTPException, status
from loguru import logger

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


async def is_user_owner(current_user: User, event_id: int) -> bool:
    user_id = await user.misc.get_id_by(current_user.info.username)
    organizer_id = await event.get_organizer_id_by(event_id)
    logger.debug(f"{user_id=}:{organizer_id=}")

    return user_id == organizer_id
