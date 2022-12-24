"""API для мероприятий"""


from datetime import datetime

from asyncpg import Record
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, status
from loguru import logger

from app import services
from app.dependencies import get_current_user
from app.misc import check, is_user_owner
from app.models.event import Event
from app.models.responses import CommentResponse
from app.models.user import User

router = APIRouter(tags=["event"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(
    event: Event,
    current_user: User = Depends(get_current_user),
) -> int:
    """Создание события в базе данных

    Я не успеваю создать валидации по дате. Пожалуйста не надо писать сюда ничего плохого :(((
    """

    await check(current_user, err_msg="Can't create event. User not verified!")

    return await services.event.create(username=current_user.username, event=event)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_event(
    id: int,
    current_user: User = Depends(get_current_user),
) -> int:
    """Удаление события из базы данных"""

    await check(current_user, err_msg="Can't delete event. User not verified!")
    if not await is_user_owner(current_user, event_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are can't delete this event!",
        )

    return await services.event.delete(id)


@router.get("/comment/{id}", status_code=status.HTTP_200_OK)
async def get_comments(id: int) -> list[CommentResponse]:
    """Получить все комментарии события (Доступно любому пользователю)"""

    return await services.comment.get_by_event(event=id)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_events() -> list[Record]:
    """Получение события (Доступно всем пользователям)"""

    return await services.event.get_list()


@router.post("/{event_id}/picture", status_code=status.HTTP_202_ACCEPTED)
async def upload_picture_to_event(
    event_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
) -> int:
    """Загрузка изображение в базу данных"""
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/tiff",
        "image/bmp",
        "video/webm",
    }

    if await is_user_owner(current_user, event_id=event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are can't upload photo to this event!. You are not organizator!",
        )

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Not allowed type of file. Allowed types: {allowed_types}",
        )

    contents = await file.read()
    return await services.photo.create(contents, media_type=file.content_type, event_id=event_id)


@router.get("/{event_id}/picture", status_code=status.HTTP_200_OK)
async def download_picture(event_id: int) -> Response:
    """Получение изображения в базу данных (Каждый может получить изображение по конкретному пользователю)"""

    picture, media_type = await services.photo.get(id=event_id)
    logger.info(picture)

    return Response(content=picture, media_type=media_type)


@router.post("/{event_id}/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(
    event_id: int,
    comment: str,
    current_user: User = Depends(get_current_user),
) -> int:
    """Оставить комментарий"""

    user_id = await services.user.misc.get_id_by(current_user.username)
    time = datetime.now()

    return await services.comment.create(
        event_id=event_id, user_id=user_id, comment=comment, current_datetime=time
    )


@router.get("/{event_id}/comment/{id}", status_code=status.HTTP_200_OK)
async def get_comment_by_id(
    id: int,
    event_id: int,
) -> CommentResponse:
    """Получить конкретный комментарий(события) по ID (Доступно любому пользователю)"""

    return await services.comment.get_by_id(id=id, event_id=event_id)


@router.get("/{event_id}", status_code=status.HTTP_200_OK)
async def get_event_by_id(
    event_id: int,
) -> Event:
    """Получение события (Доступно всем пользователям)"""

    return await services.event.get(event_id)
