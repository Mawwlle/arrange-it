from fastapi import APIRouter, status
from fastapi.params import Depends

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models import representation

router = APIRouter(tags=["role"])


@router.post("/role", status_code=status.HTTP_201_CREATED)
async def create_role(
    role: str,
    current_user: representation.User | None = Depends(get_current_user),
):
    if not current_user:
        raise anauthorized_exception

    await services.role.create(role)
