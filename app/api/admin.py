# верификация пользователей
# верификация мероприятий
# удаление пользователей

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import representation
from app.models.responses import VerificationResponse

router = APIRouter(tags=["admin"])


@router.delete("/user")
async def deleting_user(
    username: str, current_user: representation.User | None = Depends(get_current_user)
) -> representation.User:
    """Удаление конкретного пользователя"""
    pass


@router.delete("/other_admin")
async def deleting_admin(
    username: str, current_user: representation.User | None = Depends(get_current_user)
) -> representation.User:
    """Удаление других мероприятий"""

    pass


@router.post("/verify/event")
async def verify_event(
    event: int, current_user: representation.User | None = Depends(get_current_user)
) -> VerificationResponse:
    """Верификация мероприятий"""
    pass


@router.post("/verify/user")
async def verify_event(
    username: str, current_user: representation.User | None = Depends(get_current_user)
) -> VerificationResponse:
    """Верификация мероприятий"""
    pass
