import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.db.session import engine
from app.models.base import Base
from app.models import device, measurement, alert  # noqa: F401 — 테이블 등록용 import

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    목적: 앱 시작/종료 시 DB 테이블 생성 및 자원 해제.
    Side Effects: 테이블이 없으면 자동 생성 (개발 환경용).
    """
    logger.info("LabGuard 백엔드 시작")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # measurements 테이블을 TimescaleDB Hypertable로 변환
        # if_not_exists => TRUE: 이미 변환된 경우 오류 없이 스킵
        await conn.execute(text(
            "SELECT create_hypertable('measurements', 'time', if_not_exists => TRUE)"
        ))
        logger.info("TimescaleDB Hypertable 설정 완료")
    yield
    logger.info("LabGuard 백엔드 종료")
    await engine.dispose()


app = FastAPI(
    title="LabGuard API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # 프론트 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    """목적: 서버 상태 확인용 헬스체크 엔드포인트."""
    return {"status": "ok"}
