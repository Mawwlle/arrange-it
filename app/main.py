from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette import status

from app import api
from app.dependencies.db import database_pool

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8081",
    "*",
]


app = FastAPI(title="Arrange IT API. Open platform to register your meets and events.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Connecting to db")
    await database_pool.connect()

    logger.info("Connected")
    logger.info("Server Started")


@app.on_event("shutdown")
async def shutdown_event():
    await database_pool.close()

    logger.info("Server Shutted down")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
