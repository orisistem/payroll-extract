from loguru import logger

# from app.config import settings
from prisma import Prisma

prisma = Prisma()


async def init_db():
    logger.info("🔌 Connecting to database...")
    await prisma.connect()
    logger.info("✅ Database connected successfully.")


async def close_db():
    if prisma.is_connected():
        await prisma.disconnect()
        logger.info("🔒 Database connection closed.")
