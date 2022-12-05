from fastapi import FastAPI
from loguru import logger

from app import api
from app.dependencies.db import database_pool

app = FastAPI(title="Arrange IT API. Open platform to register your meets and events.")

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
