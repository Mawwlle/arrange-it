"""API для рангов"""

from fastapi import APIRouter, Security, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models.user import User

router = APIRouter(tags=["rank"])


@router.post("/rank", status_code=status.HTTP_201_CREATED)
async def create_rank(
    rank: str,
    description: str,
    current_user: User = Security(get_current_user, scopes=["administrator"]),
) -> None:
    """Создание ранга в базе данных"""

    if not current_user:
        raise anauthorized_exception

    await services.rank.create(rank, description)
