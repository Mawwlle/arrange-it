from fastapi import APIRouter

from app.api import admin, auth, event, place, rank, registration, role, tag, user

router = APIRouter()

router.include_router(user.router, prefix="/users")
router.include_router(rank.router, prefix="/ranks")
router.include_router(role.router, prefix="/roles")
router.include_router(event.router, prefix="/events")
router.include_router(auth.router)
router.include_router(admin.router, prefix="/admins")
router.include_router(registration.router, prefix="/subscriptions")
router.include_router(place.router, prefix="/places")
router.include_router(tag.router, prefix="/tags")
