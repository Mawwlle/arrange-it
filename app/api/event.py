"""API для мероприятий"""

from xml.dom import ValidationErr

from asyncpg import Record
from fastapi import APIRouter, HTTPException, Response, Security, UploadFile, status
from loguru import logger
from pydantic import ValidationError

from app import services
from app.dependencies import anauthorized_exception, get_current_user
from app.misc import check, is_user_owner
from app.models.event import Comment, Event
from app.models.user import User

router = APIRouter(tags=["event"])


@router.post("/event", status_code=status.HTTP_201_CREATED)
async def create_event(
    event: Event,
    current_user: User = Security(get_current_user, scopes=["organizer"]),
) -> int:
    """Создание события в базе данных"""

    await check(current_user, err_msg="Can't create event. User not verified!")

    return await services.event.create(username=current_user.info.username, event=event)


@router.delete("/event", status_code=status.HTTP_200_OK)
async def delete_event(
    id: int,
    current_user: User = Security(get_current_user, scopes=["organizer"]),
) -> int:
    """Удаление события из базы данных"""

    await check(current_user, err_msg="Can't delete event. User not verified!")
    await is_user_owner(current_user, event_id=id)

    return await services.event.delete(id)


@router.get("/event/{id}", status_code=status.HTTP_200_OK)
async def get_event_by_id(
    id: int,
) -> Event:
    """Получение события (Доступно всем пользователям)"""

    return await services.event.get(id)


@router.get("/event", status_code=status.HTTP_200_OK)
async def get_events() -> list[Record]:
    """Получение события (Доступно всем пользователям)"""

    return await services.event.get_list()


@router.post("/event/picture", status_code=status.HTTP_202_ACCEPTED)
async def upload_picture_to_event(
    event_id: int,
    file: UploadFile,
    current_user: User = Security(get_current_user, scopes=["organizer"]),
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

    if not current_user:
        raise anauthorized_exception

    await is_user_owner(current_user, event_id=event_id)

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Not allowed type of file. Allowed types: {allowed_types}",
        )

    contents = await file.read()
    return await services.photo.create(contents, media_type=file.content_type, event_id=event_id)


@router.get("/event/picture", status_code=status.HTTP_200_OK)
async def download_picture(event_id: int) -> Response:
    """Получение изображения в базу данных (Каждый может получить изображение по конкретному пользователю)"""
    logger.debug("Im here")
    picture, media_type = await services.photo.get(id=event_id)
    logger.info(picture)

    return Response(content=picture, media_type=media_type)


@router.post("/event/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: Comment,
    current_user: User = Security(get_current_user, scopes=["organizer", "subscriber"]),
) -> str:
    """Оставить комментарий"""

    await check(current_user, err_msg="Can't delete event. User not verified!")

    return "comment created"
