from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Security, status
from loguru import logger

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.misc import check, is_user_owner
from app.models.subscription import SubscribtionResponse
from app.models.user import User
from app.services import user

router = APIRouter(tags=["event - subscription - registration"])


@router.post("/subscribe")
async def subscription_to_event(
    id: int,
    current_user: User = Security(get_current_user, scopes=["subscriber"]),
) -> SubscribtionResponse:
    """Пользователь подписывается на мероприятие"""

    if not current_user:
        raise anauthorized_exception

    await is_user_owner(current_user, event_id=id)

    return await services.user.event.subscribe(user=current_user, event_id=id)


@router.delete("/subscribe")
async def unsubscribe_from_event(
    id: int,
    current_user: User = Security(get_current_user, scopes=["subscriber"]),
) -> SubscribtionResponse:
    """Пользователь отписывается от мероприятия"""

    if not current_user:
        raise anauthorized_exception

    await is_user_owner(current_user, event_id=id)

    now = datetime.now().date()
    event_date = await services.event.get_event_date(id)
    days_left = event_date - now

    logger.debug(f"Days to event: {days_left < timedelta(days=3)}")

    if days_left < timedelta(days=3):  # если до мероприятия меньше 3 дней!
        await user.downgrade_rating(current_user)

    return await user.event.unsubscribe(event_id=id, user=current_user)


@router.patch("/subscribe")
async def user_visited_event(
    event: int,
    current_user: User = Security(get_current_user, scopes=["organizer"]),
) -> SubscribtionResponse:
    """Пользователь посетил от мероприятие (организатор подтверждает, что пользователь посетил мероприятиe)"""

    await check(current_user, err_msg="Can't delete event. User not verified!")
    await is_user_owner(
        event_id=event, current_user=current_user
    )  # только организатор может это подтвердить

    await user.upgrade_rating(current_user)

    return await user.event.visited(event_id=event, user=current_user)
