import asyncpg
from fastapi import APIRouter, Depends, Request

from app.dependencies import get_current_user
from app.models import representation

router = APIRouter(tags=["rank"])


@router.post("/rank")
async def create_rank(
    # request: Request,
    rank: str,
    # current_user: representation.User | None = Depends(get_current_user),
):
    await request.app.db.execute('INSERT INTO "rank"(designation) VALUES ($1)', rank)
