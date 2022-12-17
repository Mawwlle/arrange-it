from fastapi import APIRouter

from app.api import event, rank, role, user

router = APIRouter()

router.include_router(user.router)
router.include_router(rank.router)
router.include_router(role.router)
router.include_router(event.router)
