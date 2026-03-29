import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """
    목적: FastAPI 의존성 주입용 DB 세션 제공.
    Returns: AsyncSession
    Side Effects: 요청 종료 시 세션 자동 닫힘.
    Raises: SQLAlchemyError - DB 연결 실패 시.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("DB 세션 오류: %s", e, exc_info=True)
            raise
