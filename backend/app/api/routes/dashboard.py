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
    alert_device_count: int  # 현재 이상 상태인 장비 수 (쿨다운 내 알림 발생)


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    """
    목적: 대시보드 상단 통계 요약 데이터를 반환합니다.
    Returns: DashboardSummary (전체 장비 수, 전체 알림 수, 현재 이상 장비 수).
    Raises: 500 - DB 오류.
    """
    try:
        total_devices = (await db.execute(select(func.count()).select_from(Device))).scalar()
        alert_count = (await db.execute(select(func.count()).select_from(AlertEvent))).scalar()

        # 현재 이상 장비 수: 최근 알림이 있는 고유 장비 수
        alert_device_count = (
            await db.execute(
                select(func.count(func.distinct(AlertEvent.device_id))).select_from(AlertEvent)
                .where(AlertEvent.notified == False)  # noqa: E712
            )
        ).scalar()

        return DashboardSummary(
            total_devices=total_devices or 0,
            alert_count=alert_count or 0,
            alert_device_count=alert_device_count or 0,
        )
    except Exception as e:
        logger.error("대시보드 요약 조회 실패: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="대시보드 데이터를 불러오지 못했습니다.")
