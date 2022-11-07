import asyncpg
from fastapi import APIRouter, Request
from fastapi.params import Depends

from app.dependencies import get_current_user, is_user_logged_in
from app.models import representation

router = APIRouter(tags=["role"])


@router.post("/role")
async def create_role(
    request: Request,
    role: str,
    # current_user: representation.User | None = Depends(get_current_user),
):
    await request.app.state.db.execute('INSERT INTO "role"(name) VALUES ($1)', role)
