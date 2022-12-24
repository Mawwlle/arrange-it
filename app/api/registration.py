from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Security, status
from loguru import logger

from app import services
from app.dependencies import anauthorized_exception, get_current_user, get_user_db
from app.misc import check, is_user_owner
from app.models.subscription import SubscribtionResponse
from app.models.user import User
from app.services import user
from app.services.user import misc
from app.services.user.event import is_currently_user_subscribed_to_event

router = APIRouter(tags=["event - subscription"])


@router.post("/{event}")
async def subscription_to_event(
    event: int,
    current_user: User = Depends(get_current_user),
) -> SubscribtionResponse:
    """Пользователь подписывается на мероприятие"""

    if await is_user_owner(current_user, event_id=event):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are can't subscribe to own event!",
        )

    return await services.user.event.subscribe(user=current_user, event_id=event)


@router.delete("/{event}")
async def unsubscribe_from_event(
    event: int,
    current_user: User = Depends(get_current_user),
) -> SubscribtionResponse:
    """Пользователь отписывается от мероприятия"""

    if await is_user_owner(current_user, event_id=event):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are can't unsubscribe from this event! You are orgaizer. Maybe remove this event?",
        )

    now = datetime.now().date()
    event_date = await services.event.get_event_date(event)
    days_left = event_date - now

    logger.debug(f"Days to event: {days_left < timedelta(days=3)}")

    if days_left < timedelta(days=3):  # если до мероприятия меньше 3 дней!
        await user.downgrade_rating(current_user)

    return await user.event.unsubscribe(event_id=event, user=current_user)


@router.patch("/{username}/visiting/{event}")
async def user_visited_event(
    username: str,
    event: int,
    current_user: User = Depends(get_current_user),
) -> SubscribtionResponse:
    """Пользователь посетил от мероприятие (организатор подтверждает, что пользователь посетил мероприятиe)"""

    user_db = await get_user_db(username)

    await check(current_user, err_msg="Can't delete event. User not verified!")

    if not await is_user_owner(
        event_id=event, current_user=current_user
    ):  # только организатор может это подтвердить
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only organizator can change it!",
        )

    user_repr = user_db.to_representation()

    if not await is_currently_user_subscribed_to_event(event_id=event, user=user_repr):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not subscribed to event!"
        )

    resp = await user.event.visited(event_id=event, user=user_repr)

    await user.upgrade_rating(user_db.id)

    return resp
