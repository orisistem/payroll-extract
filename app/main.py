from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.api.v1.routers import payroll_router
from app.config import settings
from app.infrastructure.database.prisma_client import close_db, init_db


@asynccontextmanager
async def startup(app: FastAPI):
    logger.info(f"🚀 Starting {settings.app_name} in {settings.environment} mode...")
    await init_db()
    yield
    await close_db()
    logger.info("🧹 Closing database connection...")


app = FastAPI(title=settings.app_name, lifespan=startup)

app.include_router(payroll_router.router)
