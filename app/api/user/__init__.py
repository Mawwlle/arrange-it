from fastapi import APIRouter, Depends

from app.api.user import auth
from app.dependencies import get_current_user, is_user_logged_in
from app.models import representation
from app.services.user import get_user_list, get_user_repr

router = APIRouter(tags=["user"])
router.include_router(auth.router, prefix="/auth")


@router.get("/user")
async def user(
    username: str, current_user: representation.User | None = Depends(get_current_user)
) -> representation.User:
    await is_user_logged_in(current_user)
    return await get_user_repr(username)


@router.get("/user_list")
async def get_list(
    current_user: representation.User | None = Depends(get_current_user),
) -> list[representation.User]:
    await is_user_logged_in(current_user)

    return await get_user_list()
