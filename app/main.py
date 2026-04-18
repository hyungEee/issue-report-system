from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.settings import router as settings_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logger import setup_logger, get_logger
from app.scheduler import runner

setup_logger()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("애플리케이션 시작")
    init_db()
    logger.info("DB 초기화 완료")
    runner.start()
    yield
    runner.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router)
app.include_router(settings_router)
