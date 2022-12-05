from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

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
