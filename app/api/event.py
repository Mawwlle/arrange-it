"""API для мероприятий"""

from fastapi import APIRouter, HTTPException, Security, status
from loguru import logger

from app.dependencies import anauthorized_exception, get_current_user
from app.models.user import User

router = APIRouter(tags=["event"])


@router.post("/event", status_code=status.HTTP_201_CREATED)
async def create_event(
    current_user: User = Security(get_current_user, scopes=["organizer"]),
) -> str:
    """Создание события в базе данных"""

    if not current_user:
        raise anauthorized_exception

    if not current_user.meta.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not verified user for creation events",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return "event created"
