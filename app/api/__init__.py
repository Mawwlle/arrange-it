from fastapi import APIRouter

from app.api import admin, auth, event, place, rank, registration, role, tag, user

router = APIRouter()

router.include_router(user.router)
router.include_router(rank.router)
router.include_router(role.router)
router.include_router(event.router)
router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(registration.router)
router.include_router(place.router)
router.include_router(tag.router)
