from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.models import representation

router = APIRouter(tags=["rank"])


@router.post("/rank", status_code=status.HTTP_201_CREATED)
async def create_rank(
    rank: str,
    current_user: representation.User | None = Depends(get_current_user),
):
    if not current_user:
        raise anauthorized_exception

    await services.rank.create(rank)
