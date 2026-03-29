import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.models.device import Device
from app.models.alert import AlertEvent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardSummary(BaseModel):
    total_devices: int
    alert_count: int
    unnotified_alert_count: int


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    """
    목적: 대시보드 상단 통계 요약 데이터를 반환합니다.
    Returns: DashboardSummary (전체 장비 수, 알림 수, 미확인 알림 수).
    Raises: 500 - DB 오류.
    """
    try:
        total_devices = (await db.execute(select(func.count()).select_from(Device))).scalar()
        alert_count = (await db.execute(select(func.count()).select_from(AlertEvent))).scalar()
        unnotified = (
            await db.execute(
                select(func.count()).select_from(AlertEvent).where(AlertEvent.notified == False)  # noqa: E712
            )
        ).scalar()

        return DashboardSummary(
            total_devices=total_devices or 0,
            alert_count=alert_count or 0,
            unnotified_alert_count=unnotified or 0,
        )
    except Exception as e:
        logger.error("대시보드 요약 조회 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="대시보드 데이터를 불러오지 못했습니다.")
