from fastapi import FastAPI
from loguru import logger

from app import api
from app.dependencies import Database

app = FastAPI(title="Arrange IT API. Open platform to register your meets and events.")

app.include_router(api.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Start initializing server.")
    database_instance = Database(
        user="postgres", password="abc", database="postgres", host="localhost"
    )

    await database_instance.connect()
    app.state.db = database_instance
    logger.info("Server Startup")


@app.on_event("shutdown")
async def shutdown_event():
    if not app.state.db:
        await app.state.db.close()

    logger.info("Server Shutdown")
